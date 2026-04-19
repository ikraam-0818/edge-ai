import cv2
cap = cv2.VideoCapture(0)
ret, frame = cap.read()
if ret:
    cv2.imwrite('test_snapshot.jpg', frame)
    print('Saved! Size:', frame.shape)
else:
    print('Failed to capture!')
cap.release()
