use eframe::egui;
use crate::views::{home, settings};
use std::sync::mpsc::{Receiver, Sender, channel};

#[derive(PartialEq)]
pub enum View {
    Home,
    Settings,
}

// Structure pour suivre l'état de chaque geste
pub struct GestureState {
    pub name: String,
    pub is_modified: bool,
    pub category: String,
}

pub struct TouchlessApp {
    pub current_view: View,
    pub edit_state: settings::EditState,
    pub gestures: Vec<GestureState>,
    pub tx: Sender<String>,
    pub rx: Receiver<String>,
    pub is_training: bool,
}

impl Default for TouchlessApp {
    fn default() -> Self {
        let (tx, rx) = channel();
        Self {
            current_view: View::Home,
            edit_state: settings::EditState::default(),
            gestures: vec![
                GestureState { name: "Move".into(), is_modified: false, category: "Statique".into() },
                GestureState { name: "Grab".into(), is_modified: false, category: "Statique".into() },
                GestureState { name: "Click".into(), is_modified: false, category: "Statique".into() },
                GestureState { name: "Swipe".into(), is_modified: false, category: "Dynamique".into() },
                GestureState { name: "Zoom".into(), is_modified: false, category: "Dynamique".into() },
                GestureState { name: "Question".into(), is_modified: false, category: "Dynamique".into() },
            ],
            tx,
            rx,
            is_training: false,
        }
    }
}

impl eframe::App for TouchlessApp {
    fn update(&mut self, ctx: &egui::Context, _frame: &mut eframe::Frame) {
        // --- LOGIQUE DE RÉCEPTION ---
        // On utilise 'msg' pour être cohérent avec ton test plus bas
        while let Ok(msg) = self.rx.try_recv() {
            if msg.starts_with("RESET:") {
                // On extrait le nom après "RESET:"
                let g_name = &msg[6..];
                if let Some(g) = self.gestures.iter_mut().find(|g| g.name == g_name) {
                    g.is_modified = false; // On remet en gris/blanc
                }
            }
            if msg == "TRAINING_DONE" {
                self.is_training = false;
                for gesture in self.gestures.iter_mut() {
                    gesture.is_modified = false;
                }
            }
            else {
                // Si c'est un nom de geste, on marque comme modifié
                if let Some(g) = self.gestures.iter_mut().find(|g| g.name == msg) {
                    g.is_modified = true;
                }
            }
        }

        // --- ROUTAGE DES VUES ---
        match self.current_view {
            View::Home => home::show(ctx, &mut self.current_view),
            View::Settings => settings::show(
                ctx,
                &mut self.current_view,
                &mut self.edit_state,
                &mut self.gestures,
                self.tx.clone(),
                &mut self.is_training // <--- Ajout du 6ème argument manquant
            ),
        }
    }
}