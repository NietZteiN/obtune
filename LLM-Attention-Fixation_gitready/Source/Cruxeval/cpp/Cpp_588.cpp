#include<assert.h>
#include<bits/stdc++.h>
long f(std::vector<std::string> items, std::string target) {
    if (std::find(items.begin(), items.end(), target) != items.end()) {
        return std::find(items.begin(), items.end(), target) - items.begin();
    } else {
        return -1;
    }
}
int main() {
    auto candidate = f;
    assert(candidate((std::vector<std::string>({(std::string)"1", (std::string)"+", (std::string)"-", (std::string)"**", (std::string)"//", (std::string)"*", (std::string)"+"})), ("**")) == (3));
}
