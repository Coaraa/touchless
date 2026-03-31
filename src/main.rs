use eframe::egui;

fn main() -> eframe::Result<()> {
    let options = eframe::NativeOptions {
        viewport: egui::ViewportBuilder::default().with_inner_size([1200.0, 700.0]),
        ..Default::default()
    };

    // In your main function or wherever you call eframe::run_native
    eframe::run_native(
        "Touchless App",
        options,
        Box::new(|_cc| {
            // 1. Create your app
            let app = TouchlessApp::default();

            // 2. Wrap it in Box and then Ok
            Ok(Box::new(app))
        }),
    )
}

#[derive(Default)]
struct TouchlessApp {}

impl eframe::App for TouchlessApp {
    fn update(&mut self, ctx: &egui::Context, _frame: &mut eframe::Frame) {
        ctx.set_visuals(egui::Visuals::light());

        egui::CentralPanel::default().show(ctx, |ui| {
            ui.add_space(60.0);

            let color_blue = egui::Color32::from_rgb(210, 230, 255);
            let color_orange = egui::Color32::from_rgb(255, 230, 180);

            // 1. ASTUCE POUR PRENDRE TOUTE LA PLACE : 
            // On divise l'espace disponible en 5 colonnes égales
            ui.columns(5, |columns| {
                // Colonne 0 : Grab
                draw_gesture_item(&mut columns[0], "✊", "Grab", color_blue, color_orange);
                
                // Colonne 1 : Screen
                draw_gesture_item(&mut columns[1], "✌️", "Screen", color_blue, color_orange);
                
                // Colonne 2 : Move
                draw_gesture_item(&mut columns[2], "✋", "Move", color_blue, color_orange);
                
                // Colonne 3 : Click
                draw_gesture_item(&mut columns[3], "👆", "Click", color_blue, color_orange);
                
                // Colonne 4 : Swipe
                draw_gesture_item(&mut columns[4], "👋", "Swipe", color_blue, color_orange);
            });

            ui.add_space(150.0);

            ui.vertical_centered(|ui| {
                let btn_train = egui::Button::new(egui::RichText::new("Train").size(24.0))
                    .min_size(egui::vec2(150.0, 50.0))
                    .rounding(10.0)
                    .fill(color_orange);
                
                if ui.add(btn_train).clicked() {
                    println!("Lancement de l'entraînement...");
                }
            });
        });
    }
}

// 2. FONCTION POUR DESSINER COMME SUR LA MAQUETTE
// Cette fonction gère le cercle bleu (avec l'émoji géant) et le petit rectangle orange en dessous
fn draw_gesture_item(ui: &mut egui::Ui, emoji: &str, name: &str, color_blue: egui::Color32, color_orange: egui::Color32) {
    ui.vertical_centered(|ui| {
        // Le bouton circulaire avec l'émoji géant
        let circle_btn = egui::Button::new(egui::RichText::new(emoji).size(70.0))
            .min_size(egui::vec2(140.0, 140.0)) // Plus grand pour prendre de la place
            .rounding(70.0) // Arrondi parfait (la moitié de la taille)
            .fill(color_blue);
        
        if ui.add(circle_btn).clicked() {
            println!("Action: {} cliquée !", name);
        }

        ui.add_space(15.0);

        // Le label orange en dessous (on utilise un bouton "inactif" pour simuler l'encadré)
        let label_box = egui::Button::new(egui::RichText::new(name).size(20.0).color(egui::Color32::BLACK))
            .min_size(egui::vec2(100.0, 35.0))
            .fill(color_orange)
            .rounding(5.0);
        
        // On l'ajoute à l'UI sans faire de "if clicked()" car c'est juste visuel
        let _ = ui.add(label_box); 
    });
}