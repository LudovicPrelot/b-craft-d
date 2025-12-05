// =====================================================
// B-CraftD v3.0 - MongoDB Setup Script
// Date: 4 décembre 2025
// Usage: mongo < mongodb_setup_v3.js
// Ou: mongosh < mongodb_setup_v3.js (MongoDB 5.0+)
// =====================================================

// Connexion à la base de données
use bcraftd;

print("🚀 B-CraftD v3.0 - Configuration MongoDB");
print("=========================================\n");

// =====================================================
// COLLECTION 1: audit_logs
// Usage: Logs d'audit complets (CRUD operations)
// TTL: 180 jours (6 mois)
// Volume estimé: 100k-1M documents
// =====================================================

print("📝 Création collection: audit_logs");

db.createCollection("audit_logs", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["user_id", "action", "table_name", "timestamp"],
      properties: {
        user_id: {
          bsonType: "int",
          description: "ID de l'utilisateur (référence PostgreSQL users.id)"
        },
        action: {
          bsonType: "string",
          enum: ["INSERT", "UPDATE", "DELETE", "SELECT"],
          description: "Type d'action effectuée"
        },
        table_name: {
          bsonType: "string",
          description: "Nom de la table concernée"
        },
        record_id: {
          bsonType: "int",
          description: "ID de l'enregistrement modifié"
        },
        old_values: {
          bsonType: "object",
          description: "Valeurs avant modification (UPDATE/DELETE)"
        },
        new_values: {
          bsonType: "object",
          description: "Valeurs après modification (INSERT/UPDATE)"
        },
        ip_address: {
          bsonType: "string",
          description: "Adresse IP de l'utilisateur"
        },
        user_agent: {
          bsonType: "string",
          description: "User agent du navigateur"
        },
        timestamp: {
          bsonType: "date",
          description: "Date et heure de l'action"
        }
      }
    }
  }
});

// Index pour performance
db.audit_logs.createIndex({ user_id: 1, timestamp: -1 });
db.audit_logs.createIndex({ table_name: 1, timestamp: -1 });
db.audit_logs.createIndex({ action: 1, timestamp: -1 });
db.audit_logs.createIndex({ record_id: 1, table_name: 1 });

// TTL Index: Suppression automatique après 180 jours
db.audit_logs.createIndex({ timestamp: 1 }, { expireAfterSeconds: 15552000 });

print("✅ audit_logs créée avec 5 index + TTL 180 jours\n");

// =====================================================
// COLLECTION 2: crafting_history
// Usage: Historique complet de tous les crafts
// Pas de TTL (données permanentes pour analytics)
// Volume estimé: 500k-5M documents
// =====================================================

print("📝 Création collection: crafting_history");

db.createCollection("crafting_history", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["user_id", "recipe_id", "crafted_at", "success"],
      properties: {
        user_id: {
          bsonType: "int",
          description: "ID de l'utilisateur"
        },
        recipe_id: {
          bsonType: "int",
          description: "ID de la recette craftée"
        },
        resource_id: {
          bsonType: "int",
          description: "ID de la ressource produite"
        },
        quantity_crafted: {
          bsonType: "int",
          minimum: 1,
          description: "Quantité craftée"
        },
        ingredients_used: {
          bsonType: "array",
          items: {
            bsonType: "object",
            required: ["resource_id", "quantity"],
            properties: {
              resource_id: { bsonType: "int" },
              quantity: { bsonType: "int" }
            }
          },
          description: "Liste des ingrédients utilisés"
        },
        workshop_id: {
          bsonType: ["int", "null"],
          description: "ID de l'atelier utilisé (si applicable)"
        },
        workshop_durability_before: {
          bsonType: ["int", "null"],
          description: "Durabilité de l'atelier avant craft"
        },
        workshop_durability_after: {
          bsonType: ["int", "null"],
          description: "Durabilité de l'atelier après craft"
        },
        profession_id: {
          bsonType: "int",
          description: "ID de la profession utilisée"
        },
        profession_level: {
          bsonType: "int",
          description: "Niveau de la profession au moment du craft"
        },
        experience_gained: {
          bsonType: "int",
          description: "XP de profession gagnée"
        },
        success: {
          bsonType: "bool",
          description: "Craft réussi ou échoué"
        },
        crafting_time_seconds: {
          bsonType: "int",
          description: "Temps de craft en secondes"
        },
        weather_bonus: {
          bsonType: "double",
          description: "Multiplicateur météo appliqué"
        },
        season_bonus: {
          bsonType: "double",
          description: "Multiplicateur saison appliqué"
        },
        mastery_bonus: {
          bsonType: "double",
          description: "Multiplicateur maîtrise appliqué"
        },
        crafted_at: {
          bsonType: "date",
          description: "Date et heure du craft"
        }
      }
    }
  }
});

// Index pour analytics
db.crafting_history.createIndex({ user_id: 1, crafted_at: -1 });
db.crafting_history.createIndex({ recipe_id: 1, crafted_at: -1 });
db.crafting_history.createIndex({ resource_id: 1, crafted_at: -1 });
db.crafting_history.createIndex({ profession_id: 1, crafted_at: -1 });
db.crafting_history.createIndex({ success: 1, crafted_at: -1 });
db.crafting_history.createIndex({ crafted_at: -1 }); // Index temporel global

print("✅ crafting_history créée avec 6 index (pas de TTL)\n");

// =====================================================
// COLLECTION 3: market_transactions
// Usage: Historique complet des transactions marché
// Pas de TTL (données permanentes pour analytics)
// Volume estimé: 1M-10M documents
// =====================================================

print("📝 Création collection: market_transactions");

db.createCollection("market_transactions", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["market_id", "seller_id", "buyer_id", "resource_id", "transaction_date"],
      properties: {
        market_id: {
          bsonType: "int",
          description: "ID de l'offre marché (PostgreSQL markets.id)"
        },
        seller_id: {
          bsonType: "int",
          description: "ID du vendeur"
        },
        buyer_id: {
          bsonType: "int",
          description: "ID de l'acheteur"
        },
        resource_id: {
          bsonType: "int",
          description: "ID de la ressource échangée"
        },
        quantity: {
          bsonType: "int",
          minimum: 1,
          description: "Quantité échangée"
        },
        unit_price: {
          bsonType: "double",
          description: "Prix unitaire"
        },
        total_price: {
          bsonType: "double",
          description: "Prix total de la transaction"
        },
        seller_coins_before: {
          bsonType: "double",
          description: "Coins du vendeur avant transaction"
        },
        seller_coins_after: {
          bsonType: "double",
          description: "Coins du vendeur après transaction"
        },
        buyer_coins_before: {
          bsonType: "double",
          description: "Coins de l'acheteur avant transaction"
        },
        buyer_coins_after: {
          bsonType: "double",
          description: "Coins de l'acheteur après transaction"
        },
        listing_duration_hours: {
          bsonType: "double",
          description: "Durée de l'offre avant vente (en heures)"
        },
        market_fee: {
          bsonType: "double",
          description: "Frais de marché prélevés (si applicable)"
        },
        transaction_date: {
          bsonType: "date",
          description: "Date et heure de la transaction"
        },
        created_at: {
          bsonType: "date",
          description: "Date création de l'offre"
        }
      }
    }
  }
});

// Index pour analytics économiques
db.market_transactions.createIndex({ seller_id: 1, transaction_date: -1 });
db.market_transactions.createIndex({ buyer_id: 1, transaction_date: -1 });
db.market_transactions.createIndex({ resource_id: 1, transaction_date: -1 });
db.market_transactions.createIndex({ transaction_date: -1 }); // Tendances temporelles
db.market_transactions.createIndex({ unit_price: 1, resource_id: 1 }); // Analyse prix

print("✅ market_transactions créée avec 5 index (pas de TTL)\n");

// =====================================================
// COLLECTION 4: user_metrics (Time-Series)
// Usage: Métriques utilisateurs en continu (1 doc/heure/user)
// TTL: 90 jours (3 mois)
// Volume estimé: 2M-20M documents
// =====================================================

print("📝 Création collection: user_metrics (time-series)");

db.createCollection("user_metrics", {
  timeseries: {
    timeField: "timestamp",
    metaField: "user_id",
    granularity: "hours"
  }
});

// Note: Les time-series collections ont des validateurs limités
// La structure attendue est documentée ici:
// {
//   user_id: int,           // metaField
//   timestamp: Date,         // timeField
//   level: int,
//   experience: int,
//   coins: double,
//   active_professions: int,
//   total_profession_levels: int,
//   inventory_slots_used: int,
//   inventory_total_value: double,
//   active_market_listings: int,
//   crafts_last_hour: int,
//   resources_gathered_last_hour: int,
//   sales_last_hour: int,
//   purchases_last_hour: int,
//   online_status: bool
// }

// Index spécifique time-series
db.user_metrics.createIndex({ "user_id": 1, "timestamp": -1 });

// TTL Index: Suppression automatique après 90 jours
db.user_metrics.createIndex({ timestamp: 1 }, { expireAfterSeconds: 7776000 });

print("✅ user_metrics créée (time-series) avec TTL 90 jours\n");

// =====================================================
// COLLECTION 5: chat_messages
// Usage: Historique des messages de chat
// TTL: 90 jours (3 mois)
// Volume estimé: 500k-5M documents
// =====================================================

print("📝 Création collection: chat_messages");

db.createCollection("chat_messages", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["user_id", "message", "channel", "sent_at"],
      properties: {
        user_id: {
          bsonType: "int",
          description: "ID de l'utilisateur"
        },
        username: {
          bsonType: "string",
          description: "Nom d'utilisateur (dénormalisé pour performance)"
        },
        message: {
          bsonType: "string",
          maxLength: 500,
          description: "Contenu du message"
        },
        channel: {
          bsonType: "string",
          enum: ["global", "trade", "profession", "guild", "whisper"],
          description: "Canal de chat"
        },
        recipient_id: {
          bsonType: ["int", "null"],
          description: "ID du destinataire (pour whispers)"
        },
        guild_id: {
          bsonType: ["int", "null"],
          description: "ID de la guilde (pour chat guilde)"
        },
        is_system_message: {
          bsonType: "bool",
          description: "Message système (événement automatique)"
        },
        sent_at: {
          bsonType: "date",
          description: "Date et heure d'envoi"
        }
      }
    }
  }
});

// Index pour récupération messages
db.chat_messages.createIndex({ channel: 1, sent_at: -1 });
db.chat_messages.createIndex({ user_id: 1, sent_at: -1 });
db.chat_messages.createIndex({ recipient_id: 1, sent_at: -1 });
db.chat_messages.createIndex({ guild_id: 1, sent_at: -1 });

// TTL Index: Suppression automatique après 90 jours
db.chat_messages.createIndex({ sent_at: 1 }, { expireAfterSeconds: 7776000 });

print("✅ chat_messages créée avec 5 index + TTL 90 jours\n");

// =====================================================
// VÉRIFICATION DE LA CONFIGURATION
// =====================================================

print("\n📊 Résumé de la Configuration MongoDB");
print("======================================");

const collections = db.getCollectionNames();
print(`\n✅ Collections créées: ${collections.length}`);
collections.forEach(col => print(`   - ${col}`));

print("\n📈 Index créés:");
collections.forEach(col => {
  const indexes = db.getCollection(col).getIndexes();
  print(`   ${col}: ${indexes.length} index`);
});

print("\n🔒 Validateurs JSON Schema actifs:");
const collectionsWithValidators = ["audit_logs", "crafting_history", "market_transactions", "chat_messages"];
print(`   ${collectionsWithValidators.length} collections avec validation`);

print("\n⏰ TTL Index configurés:");
print("   - audit_logs: 180 jours");
print("   - user_metrics: 90 jours");
print("   - chat_messages: 90 jours");

print("\n📦 Collections time-series:");
print("   - user_metrics (granularité: hours)");

print("\n💾 Estimation espace disque (1 an, 10k users):");
print("   - audit_logs: ~5 GB");
print("   - crafting_history: ~10 GB");
print("   - market_transactions: ~15 GB");
print("   - user_metrics: ~2 GB (rotation 90j)");
print("   - chat_messages: ~3 GB (rotation 90j)");
print("   TOTAL: ~35 GB");

// =====================================================
// DONNÉES DE TEST (optionnel)
// =====================================================

print("\n🧪 Insertion de données de test...");

// Test audit_logs
db.audit_logs.insertOne({
  user_id: 1,
  action: "INSERT",
  table_name: "users",
  record_id: 1,
  new_values: { login: "test_user", email: "test@bcraftd.com" },
  ip_address: "127.0.0.1",
  user_agent: "Mozilla/5.0",
  timestamp: new Date()
});

// Test crafting_history
db.crafting_history.insertOne({
  user_id: 1,
  recipe_id: 1,
  resource_id: 10,
  quantity_crafted: 5,
  ingredients_used: [
    { resource_id: 1, quantity: 10 },
    { resource_id: 2, quantity: 5 }
  ],
  profession_id: 1,
  profession_level: 25,
  experience_gained: 50,
  success: true,
  crafting_time_seconds: 120,
  weather_bonus: 1.2,
  season_bonus: 1.0,
  mastery_bonus: 1.1,
  crafted_at: new Date()
});

// Test market_transactions
db.market_transactions.insertOne({
  market_id: 1,
  seller_id: 1,
  buyer_id: 2,
  resource_id: 10,
  quantity: 5,
  unit_price: 100.50,
  total_price: 502.50,
  seller_coins_before: 1000.00,
  seller_coins_after: 1502.50,
  buyer_coins_before: 2000.00,
  buyer_coins_after: 1497.50,
  listing_duration_hours: 2.5,
  transaction_date: new Date(),
  created_at: new Date()
});

// Test user_metrics (time-series)
db.user_metrics.insertOne({
  user_id: 1,
  timestamp: new Date(),
  level: 15,
  experience: 1500,
  coins: 1502.50,
  active_professions: 2,
  total_profession_levels: 45,
  inventory_slots_used: 23,
  inventory_total_value: 5000.00,
  active_market_listings: 3,
  crafts_last_hour: 5,
  resources_gathered_last_hour: 12,
  sales_last_hour: 1,
  purchases_last_hour: 0,
  online_status: true
});

// Test chat_messages
db.chat_messages.insertOne({
  user_id: 1,
  username: "test_user",
  message: "Bonjour le monde !",
  channel: "global",
  is_system_message: false,
  sent_at: new Date()
});

print("✅ 5 documents de test insérés\n");

// =====================================================
// STATISTIQUES FINALES
// =====================================================

print("\n📊 Statistiques des Collections");
print("================================");

collections.forEach(col => {
  const stats = db.getCollection(col).stats();
  print(`\n${col}:`);
  print(`   Documents: ${stats.count}`);
  print(`   Taille: ${(stats.size / 1024).toFixed(2)} KB`);
  print(`   Index: ${stats.nindexes}`);
});

print("\n✅ Configuration MongoDB terminée avec succès !");
print("================================================\n");

print("🔗 Prochaines étapes:");
print("   1. Implémenter LoggingService Python (services/logging_service.py)");
print("   2. Tester connexion Python ↔ MongoDB");
print("   3. Configurer archivage automatique PostgreSQL → MongoDB");
print("   4. Monitorer performances (MongoDB Compass / mongotop)");

print("\n💡 Commandes utiles:");
print("   - Vérifier TTL: db.audit_logs.getIndexes()");
print("   - Stats collection: db.audit_logs.stats()");
print("   - Compter docs: db.audit_logs.countDocuments()");
print("   - Purge manuelle: db.audit_logs.deleteMany({ timestamp: { $lt: new Date('2024-01-01') } })");
