import glob
import pandas as pd

pd.options.display.float_format = "{:,.2f}".format


print("*===========================================================*")
print("║                                                           ║")
print("║         PROCESAMIENTO DE CORTE DIRECTO (CISSHEAR)         ║")
print("║             ~ Elaborado por F. Franco Alva ~              ║")
print("║                     ffrancoa@uni.pe                       ║")
print("║                                                           ║")
print("*===========================================================*")

# 1) Elección de archivo

print("\nI. SELECCIÓN DE ARCHIVO - - - - - - - - - - - - - - - - - - -\n")
print("- Se encontraron los siguientes archivos:")

files = []
nfiles = 0

for count, file in enumerate(glob.glob("*.HTD")):
    print("    {}) {}".format(count + 1, file))
    files.append(file)
    nfiles += 1

print()
choose = input("> Ingrese el índice del archivo a procesar: ")

try:
    choose = int(choose)
except ValueError:
    print("\n! E: Índice de archivo no válido.\n")
    input()
    exit()

if not 0 < choose <= nfiles:
    print("\n! E: Índice de archivo no válido.\n")
    input()
    exit()

file = open(files[choose - 1], "r")

# 2) Recorrido del archivo
horload = []
hordisp = []
verdisp = []

for linenumber, line in enumerate(file):
    if linenumber == 0:
        name = line.strip()
    elif linenumber == 1:
        speed = float(line.split(",")[12])
        nregs = 0
    else:
        data = line.split(",")

        horload.append(float(data[4]))
        hordisp.append(float(data[8]))
        verdisp.append(float(data[12]))

        nregs += 1

print()
print("- Nombre del archivo: {}".format(name))
print("- Número de registros: {}".format(nregs))
print("- Velocidad de deformación: {:.2f} mm/min\n".format(speed))

choose = input("* ¿Desea continuar con el procesamiento? (s/n): ")

if choose.upper() == "S":
    pass
else:
    exit()

# 3) Organización de información

data = pd.DataFrame()

data["despl. hor. [mm]"] = hordisp
data["fuerza hor. [kN]"] = horload
data["despl. ver. [mm]"] = verdisp

data = data[data["fuerza hor. [kN]"] > 0].reset_index(drop=True)

print(
    "\nII. CUADRO RESUMEN (INPUT): - - - - - - - - - - - - - - - - -\
    \n\n{}".format(
        data
    )
)

# Corrección para fuerza horizontal igual a 0

hordisp0 = data.iloc[1, 1] - data.iloc[0, 1]
hordisp0 /= data.iloc[1, 0] - data.iloc[0, 0]
hordisp0 = data.iloc[0, 1] / hordisp0
hordisp0 = data.iloc[0, 0] - hordisp0

toprow = pd.DataFrame(
    {
        "despl. hor. [mm]": round(hordisp0, 3),
        "fuerza hor. [kN]": 0.0,
        "despl. ver. [mm]": data.iloc[0, 2],
    },
    index=[0],
)

data = pd.concat([toprow, data[:]]).reset_index(drop=True)
data["despl. hor. [mm]"] -= data.iloc[0, 0]

# 4) Procesamiento

print("\nIII. REGISTRO DE DATOS DEL ENSAYO - - - - - - - - - - - - - -\n")

D = input("> Ingrese el diámetro (D) del espécimen en cm = ")

if not D:
    print("* Se asume D = 6.00 cm")
    D = 60
else:
    D = float(D) * 10

h_o = input("\n> Ingrese la altura inicial del espécimen (h_o) en cm = ")

if not h_o:
    print("* Se asume h_o = 2.50 cm\n")
    h_o = 25
else:
    h_o = float(h_o) * 10

h_cons = input(
    "\n> Ingrese su deformación por consolidacion en (Δh_cons) \
en mm [-] = "
)

if not h_cons:
    h_cons = data.iloc[0, 2]
    print("* Se asume Δh_cons = {:.2f} mm\n".format(h_cons))

else:
    h_cons = float(h_cons)

data["despl. ver. [mm]"] -= h_cons

data["def. hor. [%]"] = (data["despl. hor. [mm]"] / D) * 100
data["def. hor. [%]"] = round(data["def. hor. [%]"], 3)

data["def. vert. [%]"] = data["despl. ver. [mm]"] / (h_o - h_cons) * 100
data["def. vert. [%]"] = round(data["def. vert. [%]"], 3)

data["esf. hor. [kPa]"] = data["fuerza hor. [kN]"] / (3.1415 * D**2 / 4)
data["esf. hor. [kPa]"] = round(data["esf. hor. [kPa]"] * 10**6, 3)

hor_strain_range = [
    0,
    0.05,
    0.10,
    0.20,
    0.35,
    0.50,
    0.75,
    1.00,
    1.25,
    1.50,
    1.75,
    2.00,
    2.50,
    3.00,
    3.50,
    4.00,
    4.50,
    5.00,
    6.00,
    7.00,
    8.00,
    9.00,
    10.00,
    11.00,
    12.00,
    13.00,
    14.00,
    15.00,
    16.00,
    17.00,
    18.00,
    19.00,
    20.00,
    21.00,
    22.00,
    23.00,
    24.00,
    25.00,
    26.00,
    27.00,
    28.00,
    29.00,
    30.00,
]

for hor_strain in hor_strain_range:
    if hor_strain > max(data["def. hor. [%]"]):
        if hor_strain == round(max(data["def. hor. [%]"]), 0):
            data.loc[-1, "def. hor. [%]"] = hor_strain
            data = data.sort_values("def. hor. [%]").reset_index(drop=True)
            data = data.interpolate()
        else:
            break
    else:
        data.loc[-1, "def. hor. [%]"] = hor_strain
        data = data.sort_values("def. hor. [%]").reset_index(drop=True)
        data = data.interpolate()

data = data[data["def. hor. [%]"].isin(hor_strain_range)]
data = data.drop_duplicates(subset=["def. hor. [%]"], keep="first")

print()
print("IV. Cuadro final OUTPUT: - - - - - - - - - - - - - - - - - - - - - - - - - -")
print("\n\n{}".format(data))

new_filename = name + ".csv"

data.to_csv(new_filename, index=False)

print()
print("~ Data procesada en {}".format(new_filename))

input()

# Autor: Francesco Antonio Franco Alva
