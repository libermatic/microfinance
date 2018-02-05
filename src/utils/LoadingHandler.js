// @flow

export default class LoadingHandler {
  entities: Array<string>;
  constructor() {
    this.entities = [];
  }
  append(item: string) {
    this.entities.push(item);
  }
  remove(item: string) {
    const idx = this.entities.findIndex(x => x === item);
    if (idx > -1) {
      this.entities.splice(idx, 1);
    }
  }
  is_awaiting() {
    return this.entities.length !== 0;
  }
}
