import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.patches as mpatches
from scipy.optimize import fsolve


# =============================================================================
# ANOMALY CONVERSION FUNCTIONS
# =============================================================================

def mean_anomaly_from_true(true_anomaly, eccentricity):
    """Convert true anomaly to mean anomaly - handles all quadrants properly"""
    return (
        np.arctan2(
            -np.sqrt(1 - eccentricity**2) * np.sin(true_anomaly), 
            -eccentricity - np.cos(true_anomaly)
        ) + np.pi 
        - eccentricity * np.sqrt(1 - eccentricity**2) * np.sin(true_anomaly) 
        / (1 + eccentricity * np.cos(true_anomaly))
    )

def eccentric_anomaly_from_mean(mean_anomaly, eccentricity):
    """Solve Kepler's equation: M = E - e*sin(E) for E using numerical solver"""
    func = lambda E: E - eccentricity*np.sin(E) - mean_anomaly
    return fsolve(func, x0=mean_anomaly)

def true_anomaly_from_eccentric(eccentric_anomaly, eccentricity):
    """
    Convert eccentric to true anomaly using beta formulation
    From: https://ui.adsabs.harvard.edu/abs/1973CeMec...7..388B/abstract
    This avoids numerical issues with the traditional tan(E/2) formula
    """
    beta = eccentricity / (1 + np.sqrt(1 - eccentricity**2))
    return eccentric_anomaly + 2 * np.arctan2(beta * np.sin(eccentric_anomaly), 
                                            1 - beta * np.cos(eccentric_anomaly))

# def color_arc(ax, center, initial_angle, final_angle, color, arc_radius=0.3, alpha=0.6):
#    """Draw a colored arc to visualize angle measurements"""
#    if np.abs(final_angle - initial_angle) < 1e-6:
#        return
#    
#    # Handle angle wrapping for proper arc drawing
#    if final_angle < initial_angle:
#        final_angle += 2*np.pi
#        
#    angle_span = np.linspace(initial_angle, final_angle, num=50)
#    x0, y0 = center
#    x = np.append([x0], x0 + arc_radius * np.cos(angle_span))
#    y = np.append([y0], y0 + arc_radius * np.sin(angle_span))
#    ax.fill(x, y, color=color, alpha=alpha)

# =============================================================================
# ORBITAL PARAMETERS
# =============================================================================

ECCENTRICITY = 0.7      # High eccentricity to make differences visible
SEMIMAJOR = 1.0         # Semi-major axis (normalized)
semiminor = SEMIMAJOR * np.sqrt(1 - ECCENTRICITY**2)  # Semi-minor axis
focal_distance = SEMIMAJOR * ECCENTRICITY              # Distance from center to focus
num_frames = 200        # Animation frames

# Colorblind-friendly color palette
MA_COLOR = '#648FFF'  # Blue - Mean Anomaly
EA_COLOR = "#E70572"  # Magenta - Eccentric Anomaly  
TA_COLOR = '#FFB000'  # Orange - True Anomaly

print(f"Orbital Parameters:")
print(f"  Eccentricity: {ECCENTRICITY}")
print(f"  Semi-major axis: {SEMIMAJOR}")
print(f"  Semi-minor axis: {semiminor:.3f}")
print(f"  Focal distance: {focal_distance:.3f}")
print(f"  Animation frames: {num_frames}")

# =============================================================================
# ANOMALY CALCULATIONS
# =============================================================================

print("\nCalculating anomalies...")

# Mean anomaly: uniform motion from 0 to 2π
mean_anomaly = np.linspace(0, 2*np.pi, num_frames)

# Convert mean → eccentric using Kepler's equation solver
print("  Solving Kepler's equation (M → E)...")
eccentric_anomaly = np.array([eccentric_anomaly_from_mean(M, ECCENTRICITY)[0] 
                             for M in mean_anomaly])

# Convert eccentric → true using robust formula
print("  Converting eccentric to true anomaly (E → ν)...")
true_anomaly = np.array([true_anomaly_from_eccentric(E, ECCENTRICITY) 
                        for E in eccentric_anomaly])

print("  Anomaly calculations complete!")

# =============================================================================
# POSITION CALCULATIONS
# =============================================================================

# True anomaly positions: satellite's actual position (polar coords from focus)
r = SEMIMAJOR * (1 - ECCENTRICITY**2) / (1 + ECCENTRICITY * np.cos(true_anomaly))
x_true = (r * np.cos(true_anomaly)) + focal_distance  # Offset so focus is at origin
y_true = (r * np.sin(true_anomaly))

# Eccentric anomaly positions: points on auxiliary circle (centered at ellipse center)
x_eccentric = SEMIMAJOR * np.cos(eccentric_anomaly)
y_eccentric = SEMIMAJOR * np.sin(eccentric_anomaly)

# Generate static orbit curves for visualization
theta = np.linspace(0, 2*np.pi, 500)

# True orbit ellipse (what the satellite actually follows)
r_orbit = SEMIMAJOR * (1 - ECCENTRICITY**2) / (1 + ECCENTRICITY * np.cos(theta))
x_orbit = (r_orbit * np.cos(theta)) + focal_distance
y_orbit = (r_orbit * np.sin(theta))

# Auxiliary circle (mathematical construct for eccentric anomaly)
x_circle = SEMIMAJOR * np.cos(theta)
y_circle = SEMIMAJOR * np.sin(theta)

# =============================================================================
# ANIMATION SETUP
# =============================================================================
print("\nSetting up animation...")

fig, ax = plt.subplots(figsize=(14, 10))
ax.set_aspect('equal')
ax.set_xlim(-1.2*SEMIMAJOR, 2.2*SEMIMAJOR)
ax.set_ylim(-1.3*SEMIMAJOR, 1.3*SEMIMAJOR)
ax.axis('off')

# Static elements
orbit_line, = ax.plot(x_orbit, y_orbit, 'k-', lw=3, label='True Orbit (Ellipse)')
circle_line, = ax.plot(x_circle, y_circle, 'k--', lw=1, alpha=0.6, label='Auxiliary Circle')

# Key reference points
focus_point = ax.scatter([focal_distance], [0], s=200, c='red', marker='*', 
                        zorder=10, label='Focus (Sun/Earth)', edgecolor='darkred')
center_point = ax.scatter([0], [0], s=120, c='black', marker='o', 
                         zorder=10, label='Ellipse Center', edgecolor='white')

# Periapsis and apoapsis markers
periapsis_r = SEMIMAJOR * (1 - ECCENTRICITY)
apoapsis_r = SEMIMAJOR * (1 + ECCENTRICITY)
ax.scatter([focal_distance + periapsis_r], [0], s=100, c='green', marker='s', 
          zorder=8, label='Periapsis', alpha=0.7)
ax.scatter([focal_distance - apoapsis_r], [0], s=100, c='purple', marker='s', 
          zorder=8, label='Apoapsis', alpha=0.7)

# Animated elements  
satellite = ax.scatter([], [], s=150, c='black', zorder=15, edgecolor='white', linewidth=2)
true_line, = ax.plot([], [], color=TA_COLOR, lw=3, label='True Anomaly Line')
eccentric_line, = ax.plot([], [], color=EA_COLOR, lw=3, label='Eccentric Anomaly Line')
projection_line, = ax.plot([], [], 'k:', lw=2, alpha=0.8, label='E→ν Projection')

# Mean anomaly will be on the same auxiliary circle as eccentric anomaly
# Calculate mean anomaly positions on auxiliary circle
x_mean = SEMIMAJOR * np.cos(mean_anomaly)
y_mean = SEMIMAJOR * np.sin(mean_anomaly)

# Add mean anomaly point as animated element
mean_dot = ax.scatter([], [], s=120, c=MA_COLOR, zorder=12, 
                     edgecolor='white', linewidth=2, label='Mean Anomaly Point')
mean_line, = ax.plot([], [], color=MA_COLOR, lw=3, label='Mean Anomaly Line')

# =============================================================================
# ANIMATION UPDATE FUNCTION
# =============================================================================
def update(frame):
    """Update function called for each animation frame"""
    # Clear previous arc drawings
    for patch in ax.patches[:]:
        if isinstance(patch, plt.Polygon):
            patch.remove()
    
    i = frame
    E = eccentric_anomaly[i]
    M = mean_anomaly[i]  
    nu = true_anomaly[i]
    
    # Update satellite position (black dot shows actual satellite)
    satellite.set_offsets([[x_true[i], y_true[i]]])
    
    # TRUE ANOMALY: Line from focus to satellite + arc showing angle
    true_line.set_data([focal_distance, x_true[i]], [0, y_true[i]])
    # color_arc(ax, (focal_distance, 0), 0, nu, TA_COLOR, arc_radius=0.25)
    
    # ECCENTRIC ANOMALY: Line from center to auxiliary circle + arc
    eccentric_line.set_data([0, x_eccentric[i]], [0, y_eccentric[i]])
    # color_arc(ax, (0, 0), 0, E, EA_COLOR, arc_radius=0.35)
    
    # MEAN ANOMALY: Point and line on auxiliary circle + arc
    mean_dot.set_offsets([[x_mean[i], y_mean[i]]])
    mean_line.set_data([0, x_mean[i]], [0, y_mean[i]])
    # color_arc(ax, (0, 0), 0, M, MA_COLOR, arc_radius=0.45)
    
    # Projection line showing geometric relationship E → ν
    projection_line.set_data([x_eccentric[i], x_true[i]], [y_eccentric[i], y_true[i]])
    
    # Reference lines to periapsis (0° direction for each anomaly)
    ax.plot([focal_distance, focal_distance + 0.4], [0, 0], 
            color=TA_COLOR, lw=2, alpha=0.4, zorder=1)
    ax.plot([0, 0.4], [0, 0], 
            color=EA_COLOR, lw=2, alpha=0.4, zorder=1)
    ax.plot([0, 0.5], [0, 0], 
            color=MA_COLOR, lw=2, alpha=0.4, zorder=1)
    
    # Add angle value text 
    ax.text(0, -1.15*SEMIMAJOR, 
           f'M = {M*180/np.pi:.0f}°  |  E = {E*180/np.pi:.0f}°  |  ν = {nu*180/np.pi:.0f}°', 
           ha='center', va='top', fontsize=12, 
           bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.9))

# Create professional legend
handles = []
for color, label in zip([TA_COLOR, EA_COLOR, MA_COLOR], 
                       ['True Anomaly (ν)', 'Eccentric Anomaly (E)', 'Mean Anomaly (M)']):
    handles.append(mpatches.Patch(color=color, label=label))
ax.legend(handles=handles, loc='upper left', fontsize=11, framealpha=0.9)

# Add comprehensive title and explanation
# title_text = ('Orbital Anomalies')
# ax.text(0.3*SEMIMAJOR, 1.25*SEMIMAJOR, title_text, 
#        ha='center', va='center', fontsize=12, fontweight='bold',
#        bbox=dict(boxstyle="round,pad=0.5", facecolor="lightblue", alpha=0.8))

# Initialize animation elements
satellite.set_offsets([[x_true[0], y_true[0]]])
mean_dot.set_offsets([[x_mean[0], y_mean[0]]])
true_line.set_data([], [])
eccentric_line.set_data([], [])
mean_line.set_data([], [])
projection_line.set_data([], [])

# Create and run animation
ani = animation.FuncAnimation(fig, update, frames=num_frames, interval=120, repeat=True)
ani.save('Assets/Anomalies.gif', writer = 'pillow', fps = 15)

plt.tight_layout()
plt.show()
