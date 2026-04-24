use eframe::egui;
use crate::app::{View, GestureState}; // Import de GestureState

#[derive(Default)]
pub struct EditState {
    pub open: bool,
    pub gesture_name: String,
    pub category: String,
}

fn get_emoji(name: &str) -> &str {
    match name {
        "Move" => "✋",
        "Grab" => "✊",
        "Click" => "👆",
        "Swipe" => "👋",
        "Zoom" => "👋",
        "Question" => "👆",
        _ => "❓",
    }
}

pub fn show(ctx: &egui::Context, current_view: &mut View, edit_state: &mut EditState, gestures: &mut Vec<GestureState>) {
    let dark_bg = egui::Color32::from_rgb(26, 34, 44);
    let card_white = egui::Color32::from_rgb(248, 249, 250);
    let accent_dark = egui::Color32::from_rgb(33, 41, 54);
    let circle_blue = egui::Color32::from_rgb(210, 230, 255);
    let modified_gold = egui::Color32::from_rgb(255, 215, 0);

    // --- FENÊTRE POP-UP DE MODIFICATION ---
    if edit_state.open {
        egui::Window::new(format!("Modifier : {}", edit_state.gesture_name))
            .collapsible(false)
            .resizable(false)
            .anchor(egui::Align2::CENTER_CENTER, egui::vec2(0.0, 0.0))
            .show(ctx, |ui| {
                ui.vertical_centered(|ui| {
                    ui.label(format!("Catégorie : {}", edit_state.category));
                    ui.add_space(10.0);

                    if ui.button(egui::RichText::new("Capturer les données").strong()).clicked() {
                        // LOGIQUE : On trouve le geste et on le marque comme modifié
                        if let Some(g) = gestures.iter_mut().find(|g| g.name == edit_state.gesture_name) {
                            g.is_modified = true;
                            println!("Lancement de la capture pour le geste {}", g.name);

                            // On normalise en minuscule pour éviter les erreurs de majuscules (Static vs static)
                            let category_api = if edit_state.category.to_lowercase() == "statique" {
                                "static"
                            } else {
                                "dynamic"
                            };

                            // On clone pour le thread
                            let cat_for_thread = category_api.to_string();

                            std::thread::spawn(move || {
                                // Utilisation de format! pour construire l'URL dynamiquement
                                let url = format!("http://127.0.0.1:8000/{}/capture", cat_for_thread);

                                println!("Lancement de la requête API : {}", url);

                                let response = reqwest::blocking::get(url);

                                match response {
                                    Ok(res) => {
                                        if let Ok(body) = res.text() {
                                            println!("Réponse reçue : {}", body);
                                        }
                                    }
                                    Err(e) => println!("Erreur API : {}", e),
                                }
                            });
                        }
                        edit_state.open = false;
                    }

                    if ui.button("Réinitialiser").clicked() {
                        if let Some(g) = gestures.iter_mut().find(|g| g.name == edit_state.gesture_name) {
                            g.is_modified = false;
                        }
                        edit_state.open = false;
                    }

                    if ui.add(egui::Button::new("Annuler").frame(false)).clicked() {
                        edit_state.open = false;
                    }
                });
            });
    }

    let block_frame = egui::Frame::none()
        .fill(egui::Color32::from_rgb(240, 242, 245))
        .rounding(15.0)
        .inner_margin(20.0);

    egui::CentralPanel::default().frame(egui::Frame::none().fill(dark_bg)).show(ctx, |ui| {
        egui::Frame::none().inner_margin(20.0).show(ui, |ui| {
            egui::Frame::none().fill(card_white).rounding(20.0).inner_margin(30.0).show(ui, |ui| {
                ui.set_min_size(ui.available_size());

                ui.horizontal(|ui| {
                    let back_btn = egui::Button::new(egui::RichText::new("⬅ Retour").color(accent_dark).size(16.0)).frame(false);
                    if ui.add(back_btn).clicked() { *current_view = View::Home; }
                });

                ui.vertical_centered(|ui| {
                    ui.heading(egui::RichText::new("Configuration des gestes").strong().size(28.0));
                    ui.add_space(30.0);

                    ui.columns(2, |cols| {
                        // --- SECTION STATIQUE ---
                        block_frame.show(&mut cols[0], |ui| {
                            ui.set_min_height(250.0);
                            ui.vertical_centered(|ui| {
                                ui.label(egui::RichText::new("Modèles Statiques").size(18.0).strong().color(accent_dark));
                                ui.add_space(20.0);

                                let static_gestures: Vec<&GestureState> = gestures.iter().filter(|g| g.category == "Statique").collect();
                                ui.columns(3, |sub| {
                                    for (i, gesture) in static_gestures.iter().enumerate() {
                                        draw_gesture_item(&mut sub[i], get_emoji(&gesture.name), &gesture.name, circle_blue, accent_dark, modified_gold, gesture.is_modified, edit_state, "Static");
                                    }
                                });
                            });
                        });

                        // --- SECTION DYNAMIQUE ---
                        block_frame.show(&mut cols[1], |ui| {
                            ui.set_min_height(250.0);
                            ui.vertical_centered(|ui| {
                                ui.label(egui::RichText::new("Modèles Dynamiques").size(18.0).strong().color(accent_dark));
                                ui.add_space(20.0);

                                let dynamic_gestures: Vec<&GestureState> = gestures.iter().filter(|g| g.category == "Dynamique").collect();
                                ui.columns(3, |sub| {
                                    for (i, gesture) in dynamic_gestures.iter().enumerate() {
                                        draw_gesture_item(&mut sub[i], get_emoji(&gesture.name), &gesture.name, circle_blue, accent_dark, modified_gold, gesture.is_modified, edit_state, "Dynamic");
                                    }
                                });
                            });
                        });
                    });

                    ui.with_layout(egui::Layout::bottom_up(egui::Align::Center), |ui| {
                        ui.add_space(10.0);
                        if ui.add(egui::Button::new(egui::RichText::new("Démarrer l'entraînement").color(egui::Color32::WHITE).size(18.0))
                            .min_size(egui::vec2(300.0, 50.0)).rounding(25.0).fill(accent_dark)).clicked() {
                            println!("Entraînement lancé pour les modèles modifiés !");
                        }
                    });
                });
            });
        });
    });
}

// La fonction draw_gesture_item reste identique à la précédente...
fn draw_gesture_item(ui: &mut egui::Ui, emoji: &str, name: &str, circle_col: egui::Color32, accent_dark: egui::Color32, border_col: egui::Color32, is_modified: bool, edit_state: &mut EditState, category: &str) {
    ui.vertical_centered(|ui| {
        let mut btn = egui::Button::new(egui::RichText::new(emoji).size(30.0)).min_size(egui::vec2(70.0, 70.0)).rounding(35.0).fill(circle_col);
        if is_modified { btn = btn.stroke(egui::Stroke::new(2.5, border_col)); }
        if ui.add(btn).clicked() {
            edit_state.open = true;
            edit_state.gesture_name = name.to_string();
            edit_state.category = category.to_string();
        }
        ui.add_space(8.0);
        let label_fill = if is_modified { border_col } else { accent_dark };
        let label = egui::Button::new(egui::RichText::new(name).size(12.0).color(egui::Color32::WHITE)).min_size(egui::vec2(70.0, 22.0)).rounding(20.0).fill(label_fill);
        if ui.add(label).clicked() {
            edit_state.open = true;
            edit_state.gesture_name = name.to_string();
            edit_state.category = category.to_string();
        }
    });
}