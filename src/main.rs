use eframe::egui;

fn main() -> eframe::Result<()> {
    // Configuration de la fenêtre de base
    let options = eframe::NativeOptions {
        viewport: egui::ViewportBuilder::default().with_inner_size([700.0, 400.0]),
        ..Default::default()
    };
    
    // Lancement de l'application
    eframe::run_native(
        "Touchless",
        options,
        Box::new(|_cc| Box::<TouchlessApp>::default()),
    )
}

// Notre structure d'application (qui pourra stocker des variables plus tard)
#[derive(Default)]
struct TouchlessApp {}

impl eframe::App for TouchlessApp {
    // Cette fonction est appelée en boucle pour dessiner l'interface
    fn update(&mut self, ctx: &egui::Context, _frame: &mut eframe::Frame) {
        egui::CentralPanel::default().show(ctx, |ui| {
            ui.add_space(20.0);

            // Alignement horizontal pour la rangée de boutons de gestes
            ui.horizontal(|ui| {
                ui.add_space(30.0); // Marge à gauche
                
                // Création des boutons (l'astuce du \n permet de sauter une ligne)
                if ui.button("✊\nGrab").clicked() {
                    println!("Action: Grab sélectionnée !");
                }
                ui.add_space(10.0);
                if ui.button("✌️\nScreen").clicked() {
                    println!("Action: Screen sélectionnée !");
                }
                ui.add_space(10.0);
                if ui.button("✋\nMove").clicked() {
                    println!("Action: Move sélectionnée !");
                }
                ui.add_space(10.0);
                if ui.button("👆\nClick").clicked() {
                    println!("Action: Click sélectionnée !");
                }
                ui.add_space(10.0);
                if ui.button("👋\nSwipe").clicked() {
                    println!("Action: Swipe sélectionnée !");
                }
                ui.add_space(10.0);
                if ui.button("🤙\nClose").clicked() {
                    println!("Action: Close sélectionnée !");
                }
            });

            ui.add_space(150.0); // Espace vide au milieu

            // Alignement centré pour le bouton d'entraînement
            ui.vertical_centered(|ui| {
                if ui.button("Train").clicked() {
                    println!("Lancement du script d'entraînement...");
                }
            });
        });
    }
}