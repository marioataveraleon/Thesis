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
ax1.grid(True, alpha = 0.4)
ax1.set_xlim(0,1.1)
ax1.set_ylim(0,1.1)


# QV Curve
V = np.linspace(0.3, 1.2, 400)

# Parámetros de la U
V_crit = 0.7     # voltaje en el fondo de la U (límite de estabilidad)
Q_min  = -200.0  # Q en el fondo de la U (MVAr)
a      = -Q_min / (1.0 - V_crit)**2 # apertura de la U (ajusta hasta que te guste la forma)

Q = a * (V - V_crit)**2 + Q_min
r = 50
Q = Q[r:]
V = V[r:]

# Dibujamos la curva
ax2.plot(V, Q, c = "b")

# Línea Q = 0 (eje horizontal)
ax2.axhline(0, color='black', linewidth=1)

# Línea vertical en el punto crítico (dQ/dV = 0)
ax2.axvline(V_crit, color='black', linestyle='--', linewidth=1)
ax2.axvline(1, color='black', linestyle='--', linewidth=1)
ax2.scatter(V_crit,Q_min,c = "r")
ax2.annotate("PoVC",xy=(V_crit,Q_min),xytext=(V_crit,Q_min+15),color = "r", fontsize = 8)
ax2.scatter(1,0,c="r")
ax2.annotate("Operating\n point",xy=(1,0),xytext=(1.02,-15),color = "r", fontsize = 8)
ax2.annotate(
    "",
    xy=(V_crit,Q_min),
    xytext=(0.7, 0),
    arrowprops=dict(arrowstyle="<->", color="black", lw=1.5)
)
ax2.annotate("Reactive\n Margin \n Power",xy=(0.72,-100),xytext=(0.72,-100),color = "black", fontsize = 8 )
ax2.annotate(
    "",
    xy=(0.9,150),
    xytext=(1.1, 150),
    arrowprops=dict(arrowstyle="<->", color="black", lw=1.5)
)
ax2.annotate("Normal Voltage Range",xy=(1,175),xytext=(0.9,175),color = "black", fontsize = 8 )


# Etiquetas y formato
ax2.set_xlabel("Bus voltage (pu)")
ax2.set_ylabel("Q (MVAr)")
ax2.set_title("Q-V curve ")
ax2.grid(True,alpha = 0.4)
ax2.set_xlim(0.55,1.15)
ax2.set_ylim(-250,250)


op_regionQ = patches.Rectangle((0.9, -250), 0.2, 510, alpha=0.15)
ax2.add_patch(op_regionQ)

# (Opcional) marcar visualmente lado estable / inestable

ax2.text(0.95, Q_min -15, "Stable Region", ha='right', va='bottom')
ax2.text(0.65, Q_min -32, "Unstable\n Region", ha='right', va='bottom')


# Optional: vertical line at Q = 0
  
plt.tight_layout()
plt.show()





