#include<assert.h>
#include<bits/stdc++.h>
long f(std::vector<std::string> items, std::string item) {
    while (items.back() == item) {
        items.pop_back();
    }
    items.push_back(item);
    return items.size();
}
int main() {
    auto candidate = f;
    assert(candidate((std::vector<std::string>({(std::string)"bfreratrrbdbzagbretaredtroefcoiqrrneaosf"})), ("n")) == (2));
}
