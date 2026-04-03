use eframe::egui;
use crate::app::View;

pub fn show(ctx: &egui::Context, current_view: &mut View) {
    // Fond blanc pour la page des paramètres
    let main_frame = egui::Frame::none().fill(egui::Color32::WHITE).inner_margin(20.0);

    egui::CentralPanel::default().frame(main_frame).show(ctx, |ui| {
        
        // Croix de fermeture en haut à droite
        ui.horizontal(|ui| {
            ui.with_layout(egui::Layout::right_to_left(egui::Align::TOP), |ui| {
                let close_btn = egui::Button::new(egui::RichText::new("❌").size(24.0)).frame(false);
                if ui.add(close_btn).clicked() {
                    *current_view = View::Home;
                }
            });
        });

        ui.add_space(20.0);

        let color_blue = egui::Color32::from_rgb(210, 230, 255);
        let color_orange = egui::Color32::from_rgb(255, 230, 180);

        ui.columns(6, |columns| {
            draw_gesture_item(&mut columns[0], "✊", "Grab", color_blue, color_orange);
            draw_gesture_item(&mut columns[1], "✌️", "Screen", color_blue, color_orange);
            draw_gesture_item(&mut columns[2], "✋", "Move", color_blue, color_orange);
            draw_gesture_item(&mut columns[3], "👆", "Click", color_blue, color_orange);
            draw_gesture_item(&mut columns[4], "👋", "Swipe", color_blue, color_orange);
            draw_gesture_item(&mut columns[5], "➕", "Nouveau", color_blue, color_orange);
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

fn draw_gesture_item(ui: &mut egui::Ui, emoji: &str, name: &str, color_blue: egui::Color32, color_orange: egui::Color32) {
    ui.vertical_centered(|ui| {
        let circle_btn = egui::Button::new(egui::RichText::new(emoji).size(70.0))
            .min_size(egui::vec2(140.0, 140.0))
            .rounding(70.0)
            .fill(color_blue);
        
        if ui.add(circle_btn).clicked() {
            println!("Action: {} cliquée !", name);
        }

        ui.add_space(15.0);

        let label_box = egui::Button::new(egui::RichText::new(name).size(20.0).color(egui::Color32::BLACK))
            .min_size(egui::vec2(100.0, 35.0))
            .fill(color_orange)
            .rounding(5.0);
        
        let _ = ui.add(label_box); 
    });
}