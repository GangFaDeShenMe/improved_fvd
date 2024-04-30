import pytest
from improved_fvd import ImprovedFVD
from math import isclose

def test_fvd():
    current_car = ImprovedFVD.CurrentCar(speed=10.0, x=10.0, y=20.0, width=2.0, length=4.5)
    front_car = ImprovedFVD.CurrentLaneFrontCar(current_car=current_car, speed=10.0, x=20.0, y=25.0, width=2.5,
                                                length=5.0, beta=1)
    current_car_last_frame = ImprovedFVD.CurrentCar(speed=12.0, x=9.67, y=20.0, width=2.0, length=4.5)
    front_car_last_frame = ImprovedFVD.CurrentLaneFrontCar(current_car=current_car_last_frame, speed=12.0, x=19.6,
                                                           y=25.0,
                                                           width=2.0, length=4.5, beta=1)
    improved_fvd = ImprovedFVD(
        alpha=1.0,
        lambda_1=20,
        lambda_2=20,
        v_1=30,
        v_2=15,
        c_1=0.5,
        c_2=0.2,
        current_car_current_frame=current_car,
        current_lane_front_cars_current_frame=[front_car],
        fps=30,
        current_car_last_frame=current_car_last_frame,
        current_lane_front_cars_last_frame=[front_car_last_frame]
    )

    assert improved_fvd.result == 28.085958601002872





# More tests can be added for other methods and edge cases
