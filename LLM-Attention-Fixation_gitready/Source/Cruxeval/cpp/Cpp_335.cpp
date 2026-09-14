#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string text, std::string to_remove) {
    std::vector<char> new_text(text.begin(), text.end());
    if (std::find(new_text.begin(), new_text.end(), to_remove[0]) != new_text.end()) {
        auto index = std::find(new_text.begin(), new_text.end(), to_remove[0]) - new_text.begin();
        new_text.erase(new_text.begin() + index);
        new_text.insert(new_text.begin() + index, '?');
        new_text.erase(std::remove(new_text.begin(), new_text.end(), '?'), new_text.end());
    }
    return std::string(new_text.begin(), new_text.end());
}
int main() {
    auto candidate = f;
    assert(candidate(("sjbrlfqmw"), ("l")) == ("sjbrfqmw"));
}
