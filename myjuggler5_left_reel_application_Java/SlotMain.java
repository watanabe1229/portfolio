import javafx.application.Application;
import javafx.fxml.FXMLLoader;
import javafx.scene.Scene;
import javafx.stage.Stage;

public class SlotMain extends Application {
    @Override
    public void start(Stage primaryStage) throws Exception {
        primaryStage.setTitle("マイジャグラー5");
        primaryStage.setScene(new Scene(FXMLLoader.load(getClass().getResource("Slot.fxml"))));
        primaryStage.show();
    }

    public static void main(String[] args) {
        launch(args);
    }
}
