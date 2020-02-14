var  vm = new Vue({
    delimiters: ['[[', ']]'],
    el: '#vue_det',
    data: {
        firstname : "Bettina",
        lastname  : "Zotchi",
        address    : "Bad Oldesloe"},
        methods: {
            mydetails : function(){
                return "I am "+this.firstname +" "+ this.lastname + " from " + this.address;
            }
        }
})