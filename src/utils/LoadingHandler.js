export default class LoadingHandler {
  constructor() {
    this.entities = [];
  }
  append(item) {
    this.entities.push(item);
  }
  remove(item) {
    const idx = this.entities.findIndex(x => x === item);
    if (idx > -1) {
      this.entities.splice(idx, 1);
    }
  }
  is_awaiting() {
    return this.entities.length !== 0;
  }
}
