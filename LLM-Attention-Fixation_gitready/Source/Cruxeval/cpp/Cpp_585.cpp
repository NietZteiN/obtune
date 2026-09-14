#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string text) {
    int count = std::count(text.begin(), text.end(), text[0]);
    std::vector<char> ls(text.begin(), text.end());
    for (int i = 0; i < count; i++) {
        ls.erase(ls.begin());
    }
    return std::string(ls.begin(), ls.end());
}
int main() {
    auto candidate = f;
    assert(candidate((";,,,?")) == (",,,?"));
}
