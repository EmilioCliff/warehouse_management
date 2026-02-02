frappe.listview_settings["Stateless Stock Ledger Entry"] = {
	// add fields to fetch
	// add_fields: ["source_airport_code", "destination_airport_code"],
	// set default filters
	// filters: [["departure_date", "=", 1]],
	// hide_name_column: true, // hide the last column which shows the `name`
	// hide_name_filter: true, // hide the default filter field for the name column
	onload(listview) {
        listview.can_create = false;
	},
	// before_render() {
	// 	// triggers before every render of list records
	// },

	// set this to true to apply indicator function on draft documents too
	// has_indicator_for_draft: false,

	// get_indicator(doc) {
	// 	// customize indicator color
	// 	if (doc.public) {
	// 		return [__("Public"), "green", "public,=,Yes"];
	// 	} else {
	// 		return [__("Private"), "darkgrey", "public,=,No"];
	// 	}
	// },
	// primary_action() {
	// 	// triggers when the primary action is clicked
	// },
	// get_form_link(doc) {
	// 	// override the form route for this doc
	// },
	// add a custom button for each row
	// button: {
	// 	show(doc) {
	// 		return doc.reference_name;
	// 	},
	// 	get_label() {
	// 		return "View";
	// 	},
	// 	get_description(doc) {
	// 		return __("View {0}", [`${doc.reference_type} ${doc.reference_name}`]);
	// 	},
	// 	action(doc) {
	// 		frappe.set_route("Form", doc.reference_type, doc.reference_name);
	// 	},
	// },
	// format how a field value is shown
	// formatters: {
	// 	title(val) {
	// 		return val.bold();
	// 	},
	// 	public(val) {
	// 		return val ? "Yes" : "No";
	// 	},
	// },
};
