from ultralytics import YOLO

model = YOLO('best.pt')
result = model(source=0, show=True, conf=0.5)