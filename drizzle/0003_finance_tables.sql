CREATE TABLE "bankroll_session" (
	"id" integer PRIMARY KEY GENERATED ALWAYS AS IDENTITY (sequence name "bankroll_session_id_seq" INCREMENT BY 1 MINVALUE 1 MAXVALUE 2147483647 START WITH 1 CACHE 1),
	"user_id" text NOT NULL,
	"host" varchar(100) NOT NULL,
	"format" varchar(100) NOT NULL,
	"type" varchar(100),
	"stakes" varchar(100) NOT NULL,
	"date" timestamp with time zone DEFAULT now() NOT NULL,
	"session_start" timestamp with time zone NOT NULL,
	"session_end" timestamp with time zone NOT NULL,
	"buyin" integer DEFAULT 0 NOT NULL,
	"buyout" integer DEFAULT 0 NOT NULL,
	CONSTRAINT "bankroll_session_buyin_positive" CHECK ("bankroll_session"."buyin" >= 0),
	CONSTRAINT "bankroll_session_buyout_positive" CHECK ("bankroll_session"."buyout" >= 0)
);
--> statement-breakpoint
CREATE TABLE "friend_request" (
	"id" integer PRIMARY KEY GENERATED ALWAYS AS IDENTITY (sequence name "friend_request_id_seq" INCREMENT BY 1 MINVALUE 1 MAXVALUE 2147483647 START WITH 1 CACHE 1),
	"from_user_id" text NOT NULL,
	"to_user_id" text NOT NULL,
	"status" varchar(10) DEFAULT 'PENDING' NOT NULL,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL,
	"responded_at" timestamp with time zone,
	CONSTRAINT "unique_friend_request_direction" UNIQUE("from_user_id","to_user_id"),
	CONSTRAINT "no_self_friend_request" CHECK ("friend_request"."from_user_id" <> "friend_request"."to_user_id")
);
--> statement-breakpoint
CREATE TABLE "holding" (
	"id" integer PRIMARY KEY GENERATED ALWAYS AS IDENTITY (sequence name "holding_id_seq" INCREMENT BY 1 MINVALUE 1 MAXVALUE 2147483647 START WITH 1 CACHE 1),
	"portfolio_id" integer NOT NULL,
	"symbol" varchar(12) NOT NULL,
	"quantity" numeric(18, 6) DEFAULT '0' NOT NULL,
	"avg_cost" numeric(14, 4) DEFAULT '0' NOT NULL,
	"cost_basis" numeric(14, 2) DEFAULT '0' NOT NULL,
	"market_value" numeric(14, 2) DEFAULT '0' NOT NULL,
	CONSTRAINT "holding_portfolio_symbol_unique" UNIQUE("portfolio_id","symbol")
);
--> statement-breakpoint
CREATE TABLE "portfolio" (
	"id" integer PRIMARY KEY GENERATED ALWAYS AS IDENTITY (sequence name "portfolio_id_seq" INCREMENT BY 1 MINVALUE 1 MAXVALUE 2147483647 START WITH 1 CACHE 1),
	"user_id" text NOT NULL,
	"name" varchar(100) DEFAULT 'Main' NOT NULL,
	"cash" numeric(14, 2) DEFAULT '0' NOT NULL,
	"currency" varchar(3) DEFAULT 'USD' NOT NULL,
	"net_liquidity" numeric(14, 2) DEFAULT '0' NOT NULL,
	"is_public" boolean DEFAULT false NOT NULL,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL
);
--> statement-breakpoint
CREATE TABLE "portfolio_transaction" (
	"id" integer PRIMARY KEY GENERATED ALWAYS AS IDENTITY (sequence name "portfolio_transaction_id_seq" INCREMENT BY 1 MINVALUE 1 MAXVALUE 2147483647 START WITH 1 CACHE 1),
	"portfolio_id" integer NOT NULL,
	"kind" varchar(10) NOT NULL,
	"symbol" varchar(12) DEFAULT '' NOT NULL,
	"quantity" numeric(18, 6),
	"price" numeric(14, 4),
	"fee" numeric(10, 2) DEFAULT '0' NOT NULL,
	"executed_at" timestamp with time zone DEFAULT now() NOT NULL,
	"realized_gain" numeric(14, 2)
);
--> statement-breakpoint
ALTER TABLE "bankroll_session" ADD CONSTRAINT "bankroll_session_user_id_user_id_fk" FOREIGN KEY ("user_id") REFERENCES "public"."user"("id") ON DELETE cascade ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "friend_request" ADD CONSTRAINT "friend_request_from_user_id_user_id_fk" FOREIGN KEY ("from_user_id") REFERENCES "public"."user"("id") ON DELETE cascade ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "friend_request" ADD CONSTRAINT "friend_request_to_user_id_user_id_fk" FOREIGN KEY ("to_user_id") REFERENCES "public"."user"("id") ON DELETE cascade ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "holding" ADD CONSTRAINT "holding_portfolio_id_portfolio_id_fk" FOREIGN KEY ("portfolio_id") REFERENCES "public"."portfolio"("id") ON DELETE cascade ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "portfolio" ADD CONSTRAINT "portfolio_user_id_user_id_fk" FOREIGN KEY ("user_id") REFERENCES "public"."user"("id") ON DELETE cascade ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "portfolio_transaction" ADD CONSTRAINT "portfolio_transaction_portfolio_id_portfolio_id_fk" FOREIGN KEY ("portfolio_id") REFERENCES "public"."portfolio"("id") ON DELETE cascade ON UPDATE no action;--> statement-breakpoint
CREATE INDEX "bankroll_session_user_id_idx" ON "bankroll_session" USING btree ("user_id");--> statement-breakpoint
CREATE INDEX "friend_request_to_user_idx" ON "friend_request" USING btree ("to_user_id");--> statement-breakpoint
CREATE INDEX "portfolio_user_id_idx" ON "portfolio" USING btree ("user_id");--> statement-breakpoint
CREATE INDEX "portfolio_transaction_portfolio_executed_idx" ON "portfolio_transaction" USING btree ("portfolio_id","executed_at");--> statement-breakpoint
CREATE INDEX "portfolio_transaction_symbol_idx" ON "portfolio_transaction" USING btree ("symbol");