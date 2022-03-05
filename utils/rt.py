from asyncio import exceptions
from re import X
from matplotlib.pyplot import xscale
import numpy as np
import matplotlib as plt
from numpy.linalg import norm


def cross(v1, v2):
    return np.array(
        [
            v1[1] * v2[2] - v1[2] * v2[1],
            v1[2] * v2[0] - v1[0] * v2[2],
            v1[0] * v2[1] - v1[1] * v2[0],
        ]
    )


class Material:
    def __init__(
        self,
        refractive_index: float = 1,
        albedo: tuple = (2, 0, 0, 0),
        diffuse_color=np.array([0, 0, 0]),
        specular_exponent: float = 0,
    ):
        self.refractive_index = refractive_index
        self.albedo = albedo
        self.diffuse_color = diffuse_color
        self.specular_exponent = specular_exponent


class Sphere:
    def __init__(self, center, radius: float, material: Material):
        self.center = center
        self.radius = radius
        self.material = material


class Vector3:
    def __init__(self, x=0, y=0, z=0):
        self.x = x
        self.y = y
        self.z = z

    def __getitem__(self, index):
        if index == 0:
            return self.x
        elif index == 1:
            return self.y
        elif index == 2:
            return self.z
        else:
            raise Exception("Out of bounds")

    def __setitem__(self, index, value):
        if index == 0:
            self.x = value
        elif index == 1:
            self.y = value
        elif index == 2:
            self.z = value
        else:
            raise Exception("Out of bounds")

    def __mul__(self, value):
        if isinstance(value, Vector3):
            return self.x * value.x + self.y * value.y + self.z * value.z
        return Vector3(self.x * value, self.y * value, self.z * value)

    def __add__(self, value):
        return Vector3(self.x + value.x, self.y + value.y, self.z + value.z)

    def __sub__(self, value):
        return Vector3(self.x - value.x, self.y - value.y, self.z - value.z)

    def __neg__(self):
        return Vector3(-self.x, -self.y, -self.z)

    def norm(self):
        return np.sqrt(self.x**2 + self.y**2 + self.z**2)

    def normalized(self):
        return self * (1.0 / self.norm())


def vector3_to_nparray(vector: Vector3):
    return np.array([vector.x, vector.y, vector.z])


IVORY = Material(1.0, (0.9, 0.5, 0.1, 0.0), Vector3(0.4, 0.4, 0.3), 50.0)
GLASS = Material(1.5, (0.0, 0.9, 0.1, 0.8), Vector3(0.6, 0.7, 0.8), 125.0)
RED_RUBBER = Material(1.0, (1.4, 0.3, 0.0, 0.0), Vector3(0.3, 0.1, 0.1), 10.0)
MIRROR = Material(1.0, (0.0, 16.0, 0.8, 0.0), Vector3(1.0, 1.0, 1.0), 1425.0)

SPHERES = (
    Sphere(Vector3(-3, 0, -16), 2, IVORY),
    Sphere(Vector3(-1.0, -1.5, -12), 2, GLASS),
    Sphere(Vector3(1.5, -0.5, -18), 3, RED_RUBBER),
    Sphere(Vector3(7, 5, -18), 4, MIRROR),
)

LIGHTS = (Vector3(-20, 20, 20), Vector3(30, 50, -25), Vector3(30, 20, 30))


def reflect(I, N):
    return I - N * 2.0 * (I * N)


def refract(I, N, eta_t, eta_i=1.0):
    cosi = -max(-1.0, min(1.0, I * N))
    if cosi < 0:
        return refract(I, -N, eta_i, eta_t)

    eta = eta_i / eta_t
    k = 1 - eta * eta * (1 - cosi * cosi)
    if k < 0:
        return Vector3(1, 0, 0)
    return I * eta + N * (eta * cosi - np.sqrt(k))


def ray_sphere_intersect(orig, dir, s: Sphere) -> tuple:
    L = s.center - orig
    tca = L * dir
    d2 = L * L - tca * tca
    if d2 > s.radius**2:
        return (False, 0)

    thc = np.sqrt(s.radius**2 - d2)
    t0 = tca - thc
    t1 = tca + thc

    if t0 > 0.001:
        return (True, t0)
    if t1 > 0.001:
        return (True, t1)
    return (False, 0)


def scene_intersect(orig, dir) -> tuple:
    nearest_dist = 1e10
    material = Material()
    pt = Vector3()
    N = Vector3()
    if abs(dir[1]) > 0.001:
        d = -(orig[1] + 4) / dir[1]
        p = orig + dir * d
        if (
            d > 0.001
            and d < nearest_dist
            and abs(p[0]) < 10
            and p[2] < -10
            and p[2] > -30
        ):
            nearest_dist = d
            pt = p
            N = Vector3(0, 1, 0)
            if (int(0.5 * pt[0] + 1000) + int(0.5 * pt[2])) & 1:
                material.diffuse_color = Vector3(0.3, 0.3, 0.3)
            else:
                material.diffuse_color = Vector3(0.3, 0.2, 0.1)

    for sphere in SPHERES:
        intersection, d = ray_sphere_intersect(orig, dir, sphere)
        if not intersection or d > nearest_dist:
            continue

        nearest_dist = d
        pt = orig + dir * nearest_dist
        N = (pt - sphere.center).normalized()
        material = sphere.material

    return (nearest_dist < 1000, pt, N, material)


def cast_ray(orig, dir, depth=0):
    hit, point, N, material = scene_intersect(orig, dir)
    if depth > 4 or not hit:
        return Vector3(0.2, 0.7, 0.8)

    reflect_dir = (reflect(dir, N)).normalized()
    refract_dir = (refract(dir, N, material.refractive_index)).normalized()
    reflect_color = cast_ray(point, reflect_dir, depth + 1)
    refract_color = cast_ray(point, refract_dir, depth + 1)

    diffuse_light_intensity = (0,)
    specular_light_intensity = 0
    for light in LIGHTS:
        light_dir = (light - point).normalized()
        hit, shadow_pt, trashrm, trashmat = scene_intersect(point, light_dir)

        if hit and (shadow_pt - point).norm() < (light - point).norm():
            continue

        diffuse_light_intensity += max(0.0, light_dir * N)
        specular_light_intensity += pow(
            max(0.0, -reflect(-light_dir, N) * dir), material.specular_exponent
        )

    return (
        material.diffuse_color * diffuse_light_intensity * material.albedo[0]
        + Vector3(1.0, 1.0, 1.0) * specular_light_intensity * material.albedo[1]
        + reflect_color * material.albedo[2]
        + refract_color * material.albedo[3]
    )


def _main():
    width = 1280
    height = 720
    fov = 1.05

    image = np.zeros((height, width, 3))

    for i in range(height):
        for j in range(width):
            dir_x = (i + 0.5) - width / 2
            dir_y = -(j + 0.5) + height / 2
            dir_z = -height / (2.0 * np.tan(fov / 2.0))
            color = cast_ray(
                Vector3(0, 0, 0), Vector3(dir_x, dir_y, dir_z).normalized()
            )
            # maximum = max(1.0, max(color[0], max(color[1], color[2])))
            # for i in range(3):
            #     color[i] = 255 * color[i] / maximum
            # print(f"{color[0]},{color[1]},{color[2]}")
            try:
                image[i][j] = vector3_to_nparray(color)
            except Exception as e:
                pass

        print(f"{i + 1}/{height}")

    plt.imsave("text.png", image)


_main()
