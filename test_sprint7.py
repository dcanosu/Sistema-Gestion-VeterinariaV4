# import unittest
# from unittest.mock import patch
# from io import StringIO
# from sprint7 import SistemaVeterinaria, Propietario, Mascota

# class TestSistemaVeterinaria(unittest.TestCase):
#     def setUp(self):
#         self.sistema = SistemaVeterinaria()

#     @patch('builtins.input', side_effect=[
#         'Firulais',   # nombre de la mascota
#         'Perro',      # especie
#         'Labrador',   # raza
#         '3',          # edad
#         'Juan',       # nombre del dueño (no existe, así que lo registrará)
#         'Juan',       # nombre del dueño (registro)
#         '1234567890', # teléfono
#         'Calle 123'   # dirección
#     ])
#     @patch('builtins.print')  # Para suprimir los prints
#     def test_registrar_mascota(self, mock_print, mock_input):
#         self.sistema.mascotas = []
#         self.sistema.propietarios = []

#         self.sistema.registrar_mascota()

#         # Comprobamos que se registró una mascota
#         self.assertEqual(len(self.sistema.mascotas), 1)
#         mascota = self.sistema.mascotas[0]
#         self.assertEqual(mascota.nombre, "Firulais")
#         self.assertEqual(mascota.especie, "Perro")
#         self.assertEqual(mascota.raza, "Labrador")
#         self.assertEqual(mascota.edad, 3)
#         self.assertEqual(mascota.propietario.nombre, "Juan")
#         self.assertEqual(mascota.propietario.telefono, "1234567890")
#         self.assertEqual(mascota.propietario.direccion, "Calle 123")

# if __name__ == '__main__':
#     unittest.main(verbosity=2)
import unittest
from unittest.mock import patch, mock_open
from sprint6 import Mascota, Propietario, Consulta, SistemaVeterinaria
from datetime import datetime
import json

class TestVeterinaria(unittest.TestCase):
    def setUp(self):
        self.sistema = SistemaVeterinaria()
        self.prop = Propietario("Carlos", "321", "Cra 45")
        self.mascota = Mascota("Luna", "Perro", "Labrador", 5, self.prop)
        self.sistema.mascotas.append(self.mascota)
    # 1. Validar creación y atributos
    def test_creacion_propietario(self):
        p = Propietario("Ana", "123456789", "Calle Falsa")
        self.assertEqual(p.nombre, "Ana")
        self.assertEqual(p.telefono, "123456789")
        self.assertEqual(p.direccion, "Calle Falsa")

    def test_creacion_mascota(self):
        p = Propietario("Carlos", "111", "Av. Siempreviva")
        m = Mascota("Firulais", "Perro", "Labrador", 5, p)
        self.assertEqual(m.nombre, "Firulais")
        self.assertEqual(m.edad, 5)
        self.assertEqual(m.propietario.nombre, "Carlos")

    def test_creacion_consulta(self):
        p = Propietario("Laura", "999", "Cra. 45")
        m = Mascota("Michi", "Gato", "Siames", 2, p)
        fecha = datetime.today()
        c = Consulta(fecha, "Vacunación", "Sin novedad", m)
        self.assertEqual(c.motivo, "Vacunación")
        self.assertEqual(c.mascota.nombre, "Michi")

    # 2. Validar excepciones
    def test_error_edad_invalida(self):
        sistema = SistemaVeterinaria()
        with patch("builtins.input", side_effect=["Luna", "Perro", "Callejero", "dos", "3", "Pedro"]), \
             self.assertLogs('root', level='ERROR') as cm:
            with patch.object(sistema, "buscar_propietario", return_value=Propietario("Pedro", "123", "ABC")):
                sistema.registrar_mascota()
        self.assertTrue(any("Error al ingresar la edad" in m for m in cm.output))

    def test_edad_no_entero(self):
        with patch("builtins.input", side_effect=["Luna", "Perro", "Labrador", "cinco", "5", "Carlos"]), \
             self.assertLogs('root', level='ERROR') as cm:
            with patch.object(self.sistema, "buscar_propietario", return_value=self.prop):
                self.sistema.registrar_mascota()
        self.assertTrue(any("Error al ingresar la edad" in m for m in cm.output))

    def test_fecha_mal_formateada(self):
        with patch("builtins.input", side_effect=["Luna", "30/12/2024", "31-12-2024", "Revisión", "Todo bien"]), \
             self.assertLogs('root', level='ERROR') as cm:
            self.sistema.registrar_consulta()
        self.assertTrue(any("Error al ingresar la fecha" in m for m in cm.output))

    def test_error_guardar_csv(self):
        with patch("builtins.open", side_effect=IOError("No se puede escribir")), \
             self.assertLogs('root', level='ERROR') as cm:
            self.sistema.guardar_mascotas_csv(self.mascota)
        self.assertTrue(any("Error al guardar mascota en CSV" in m for m in cm.output))

    def test_error_guardar_json(self):
        consulta = Consulta(datetime.today(), "Chequeo", "Bien", self.mascota)
        self.sistema.consultas.append(consulta)

        with patch("builtins.open", side_effect=IOError("Error al guardar")), \
             self.assertLogs('root', level='ERROR') as cm:
            self.sistema.guardar_json_consultas()
        self.assertTrue(any("Error al guardar consultas en JSON" in m for m in cm.output))

    def test_error_cargar_json(self):
        with patch("builtins.open", side_effect=IOError("Error de lectura")), \
             self.assertLogs('root', level='ERROR') as cm:
            self.sistema.cargar_json("consultas.json")
        self.assertTrue(any("Error al cargar JSON" in m for m in cm.output))

    # 3. Validar logging
    def test_logging_guardar_csv(self):
        sistema = SistemaVeterinaria()
        mascota = Mascota("Max", "Perro", "Bulldog", 3, Propietario("Leo", "999", "Centro"))
        with self.assertLogs('root', level='INFO') as cm:
            sistema.guardar_mascotas_csv(mascota)
        self.assertTrue(any("guardada en archivo CSV" in m for m in cm.output))

    # 4. Serialización JSON
    def test_serializacion_json(self):
        p = Propietario("Ana", "123", "XYZ")
        m = Mascota("Kira", "Gato", "Mestizo", 4, p)
        consulta = Consulta(datetime(2024, 5, 1), "Chequeo", "Bien", m)
        json_data = json.dumps(consulta.diccionario_Consulta(), ensure_ascii=False)
        self.assertIn("Kira", json_data)
        self.assertIn("Chequeo", json_data)

    def test_deserializacion_json(self):
        dict_data = {
            "fecha": "01-05-2024",
            "motivo": "Chequeo",
            "diagnostico": "Bien",
            "mascota": {
                "nombre": "Kira",
                "especie": "Gato",
                "raza": "Mestizo",
                "edad": 4,
                "propietario": {
                    "nombre": "Ana",
                    "telefono": "123",
                    "direccion": "XYZ"
                }
            }
        }
        consulta = Consulta.from_dict(dict_data)
        self.assertEqual(consulta.mascota.nombre, "Kira")
        self.assertEqual(consulta.mascota.propietario.nombre, "Ana")
        self.assertEqual(consulta.fecha.strftime("%d-%m-%Y"), "01-05-2024")

    

if __name__ == "__main__":
    unittest.main()
