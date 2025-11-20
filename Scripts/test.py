import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches

## PV CURVE
# --- Parameters (you can change these) ---
Es = 1.05     # sending-end voltage magnitude (pu)
Z_ln = 0.5       # line impedance magnitude (pu) - used as base
theta = np.deg2rad(84.3)   # line impedance angle (deg -> rad)
phi = np.deg2rad(18.2)     # load power factor angle (lagging, deg -> rad)

# --- Sweep of load impedance (Z_LD/Z_LN) ---
k = np.linspace(0, 200, 20000)   # k = Z_LD / Z_LN Vector from 0 to 3
# --- From Kundur's simple radial model (Chap. 2 + 14.1.1) ---
# F(k) term
F = 1 + k**2 + 2 * k * np.cos(theta - phi)

# Receiving-end voltage (normalized by Es)
V_R = (k / np.sqrt(F)) * Es

# Receiving-end active power
P_R = (k/ F) * (Es / Z_ln)**2 * np.cos(phi)

# Normalize power by its maximum
P_R_max = np.max(P_R)

P_R_norm = P_R / P_R_max
PoVC = np.max(P_R_norm)

#figure
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

# ADD INFO TO PLOT
#rectange
op_region = patches.Rectangle((0,0.8),1.1,0.2,alpha = 0.15)
ax1.text(0.1,0.83,"Operating Region",fontsize=8)
ax1.add_patch(op_region) # Add the operating region
#Stable Unstable line
ax1.plot([0,1.2],[0.6,0.6],'k--')
ax1.annotate("Stable Region",(0.1,0.7),fontsize = 12)
ax1.annotate("Unstable Region",(0.1,0.5),fontsize = 12)
#Point of Voltage Collapse 
ax1.scatter(PoVC,0.6,color = "r") # add a dot in P max1
ax1.annotate("PoVC",(PoVC,0.6),xytext=(PoVC+0.01,0.62),color = "r", fontsize = 8)
# Operating point
x_op = 0.601
y_op= 0.875
ax1.scatter(x_op,y_op,color = "r")
ax1.annotate("Operating point",(x_op,y_op),xytext=(x_op-0.1,y_op-0.05),color = "r",fontsize = 8)
# MW distance to PoVC
ax1.plot([x_op,x_op],[0,1.1],"k--")
ax1.plot([PoVC,PoVC],[0,1.1],'k--')
ax1.annotate(
    "",
    xy=(x_op, y_op),
    xytext=(PoVC, y_op),
    arrowprops=dict(arrowstyle="<->", color="black", lw=1.5)
)
ax1.annotate("MW Distance to Critical Point",xy=(x_op,y_op),xytext=(x_op+0.01,y_op+0.1),color = "black", fontsize = 10 )
# Plot
ax1.plot(P_R_norm,V_R/Es,color = "b")
ax1.set_xlabel(r"Active Power $P_R/P_{R,\max1}$ ")
ax1.set_ylabel(r"Receiving end Voltage $V_R/E_S$")
ax1.set_title("PV Curve")
ax1.grid(True)
ax1.set_xlim(0,1.1)
ax1.set_ylim(0,1.1)

## QV Curve

# -------- System parameters (adjust these as needed) --------
E = Es          # Thevenin voltage (pu)
X = Z_ln          # Thevenin reactance seen from the bus (pu)
P = x_op *P_R_max          # Active power demand at the bus (pu)

# -------- Voltage sweep (candidate values for V) --------
V = np.linspace(0.3, 1.2, 600)

# Solve for delta using active power equation:
#   P = (E*V/X) * sin(delta)
sin_delta = P * X / (E * V)

# Keep only physically valid values (|sin(delta)| <= 1)
mask = np.abs(sin_delta) <= 1.0
V_valid = V[mask]
delta = np.arcsin(sin_delta[mask])

# Compute Q using:
#   Q = (E*V/X)*cos(delta) - (V^2 / X)
Q = (E * V_valid / X) * np.cos(delta) - (V_valid**2 / X)


#ax2.axvline(Q_lim, color="k", linestyle="--", linewidth=0.8)
op_regionQ = patches.Rectangle((0.7,0.9),1.1,0.2,alpha = 0.15)
#ax2.text(Q_lim,0.83,"Operating Region",fontsize=8)
ax2.add_patch(op_regionQ) # Add the operating region

# --- Plot QV curves ---

ax2.plot(Q,V_valid,color="b")
ax2.set_xlabel(r"Reactive power at receiving bus $Q$ (pu)")
ax2.set_ylabel(r"Bus voltage magnitude $V$ (pu)")
ax2.set_title(r"$Q$--$V$ Curve (fixed $P$ = %.2f pu)" % P)
ax2.grid(True)
ax2.set_xlim(0,0.5)
ax2.set_ylim(0,1)

# Optional: vertical line at Q = 0
  
plt.tight_layout()
plt.show()





