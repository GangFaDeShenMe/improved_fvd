from improved_fvd import ImprovedFVD

"""
λ1 = 40, λ2 = 20, wn+1 = wf = wr = 1.6, ln+j = lf = lr = 5, bn+j = 0.5, bf = br = 3.5, m = 3, β1 =
6/7, β2 = 6/49, β3 = 1/49, p1 = 0.8, p2 = 0.1, p3 = 0.1, q1 = 0.8, q2 = 0.1, q3 = 0.1, s1 = 0.8,
s2 = 0.1, s3 = 0.1, γ = η = 0.5 
"""

current_car_current_frame = ImprovedFVD.CurrentCar(speed=10, x=5, y=3, width=1.6, length=5,)
current_car_last_frame = ImprovedFVD.CurrentCar(speed=10, x=4.67, y=3, width=1.6, length=5,)

current_lane_front_cars_current_frame = [
    ImprovedFVD.CurrentLaneFrontCar(width=1.6, length=5, y=3 + 0.5, x=5 + 10, speed=10, beta=1, current_car=current_car_current_frame),
]
current_lane_front_cars_last_frame = [
    ImprovedFVD.CurrentLaneFrontCar(width=1.6, length=5, y=3 + 0.5, x=4.67 + 10, speed=10, beta=1, current_car=current_car_last_frame),
]

improved_fvd = ImprovedFVD(
    alpha=1,
    lambda_1=40,
    lambda_2=10,

    v_1=6.75,
    v_2=7.91,
    c_1=0.13,
    c_2=1.57,

    current_car_current_frame=current_car_current_frame,
    current_lane_front_cars_current_frame=current_lane_front_cars_current_frame,

    current_car_last_frame=current_car_last_frame,
    current_lane_front_cars_last_frame=current_lane_front_cars_last_frame,

    fps=30
)

print(improved_fvd.result)
