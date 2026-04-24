use eframe::egui;
use crate::views::{home, settings};

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
    // On stocke l'état de modification de la popup ici
    pub edit_state: settings::EditState,
    // On stocke la liste des gestes pour garder en mémoire ceux modifiés
    pub gestures: Vec<GestureState>,
}

impl Default for TouchlessApp {
    fn default() -> Self {
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
        }
    }
}

impl eframe::App for TouchlessApp {
    fn update(&mut self, ctx: &egui::Context, _frame: &mut eframe::Frame) {
        match self.current_view {
            View::Home => home::show(ctx, &mut self.current_view),
            // Ajout du paramètre &mut self.gestures
            View::Settings => settings::show(ctx, &mut self.current_view, &mut self.edit_state, &mut self.gestures),
        }
    }
}