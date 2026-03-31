use eframe::egui;

fn main() -> eframe::Result<()> {
    let options = eframe::NativeOptions {
        // 1. MODIFICATION DE LA TAILLE DE LA FENÊTRE (Largeur: 800, Hauteur: 600)
        viewport: egui::ViewportBuilder::default().with_inner_size([800.0, 600.0]),
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
        // 2. PASSAGE EN MODE CLAIR FORCÉ
        ctx.set_visuals(egui::Visuals::light());

        egui::CentralPanel::default().show(ctx, |ui| {
            ui.add_space(40.0);

            // Définition de couleurs personnalisées (Format RVB)
            // let color_blue = egui::Color32::from_rgb(210, 230, 255);
            let color_orange = egui::Color32::from_rgb(255, 230, 180);

            // On pré-calcule la taille totale de notre groupe de 5 boutons.
            // 5 boutons de 80 pixels + 4 espaces de 15 pixels entre eux
            let total_width = (80.0 * 5.0) + (15.0 * 4.0);

            ui.horizontal(|ui| {
                // 1. L'ASTUCE EST ICI : On ajoute un espace vide dynamique à gauche
                // Ça pousse tout le reste vers la droite de manière parfaitement centrée
                let espace_a_gauche = (ui.available_width() - total_width) / 2.0;
                ui.add_space(espace_a_gauche);

                // 2. On ajoute nos boutons stylisés comme avant
                let btn_grab = egui::Button::new(egui::RichText::new("✊\nGrab").size(20.0))
                    .min_size(egui::vec2(80.0, 80.0))
                    .rounding(40.0)
                    .fill(egui::Color32::from_rgb(210, 230, 255));
                if ui.add(btn_grab).clicked() {
                    println!("Action: Grab !");
                }

                ui.add_space(15.0);

                let btn_screen = egui::Button::new(egui::RichText::new("✌️\nScreen").size(20.0))
                    .min_size(egui::vec2(80.0, 80.0))
                    .rounding(40.0)
                    .fill(egui::Color32::from_rgb(210, 230, 255));
                if ui.add(btn_screen).clicked() {
                    println!("Action: Screen !");
                }

                ui.add_space(15.0);

                let btn_move = egui::Button::new(egui::RichText::new("✋\nMove").size(20.0))
                    .min_size(egui::vec2(80.0, 80.0))
                    .rounding(40.0)
                    .fill(egui::Color32::from_rgb(210, 230, 255));
                if ui.add(btn_move).clicked() {
                    println!("Action: Move !");
                }

                ui.add_space(15.0);

                let btn_click = egui::Button::new(egui::RichText::new("👆\nClick").size(20.0))
                    .min_size(egui::vec2(80.0, 80.0))
                    .rounding(40.0)
                    .fill(egui::Color32::from_rgb(210, 230, 255));
                if ui.add(btn_click).clicked() {
                    println!("Action: Click !");
                }

                ui.add_space(15.0);

                let btn_swipe = egui::Button::new(egui::RichText::new("👋\nSwipe").size(20.0))
                    .min_size(egui::vec2(80.0, 80.0))
                    .rounding(40.0)
                    .fill(egui::Color32::from_rgb(210, 230, 255));
                if ui.add(btn_swipe).clicked() {
                    println!("Action: Swipe !");
                }
            });

            

            ui.add_space(200.0);

            ui.vertical_centered(|ui| {
                // Bouton Train stylisé
                let btn_train = egui::Button::new(egui::RichText::new("Train").size(24.0))
                    .min_size(egui::vec2(150.0, 50.0)) // Bouton plus large
                    .rounding(10.0)                    // Bords légèrement arrondis
                    .fill(color_orange);               // Fond jaune/orange
                
                if ui.add(btn_train).clicked() {
                    println!("Lancement de l'entraînement...");
                }
            });
        });
    }
}