import powerfactory as pf

def main():
    app = pf.GetApplication()
    if  not app:
        raise RuntimeError("No se pudo conectar con powerfactory")
    app.ClearOutputWindow()
    app.PrintPlain("=== Test PowerFactory-Python OK ===")

if __name__ == "__main__":
    main()