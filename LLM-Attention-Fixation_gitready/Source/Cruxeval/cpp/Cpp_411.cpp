#include<assert.h>
#include<bits/stdc++.h>
bool f(std::string text, std::string pref) {
    if (pref[0] == '[') {
        std::vector<std::string> prefixes;
        size_t pos = 0;
        size_t next_pos = 0;
        while ((next_pos = pref.find(',', pos)) != std::string::npos) {
            prefixes.push_back(pref.substr(pos, next_pos - pos));
            pos = next_pos + 2;
        }
        prefixes.push_back(pref.substr(pos));

        for (const auto& x : prefixes) {
            if (text.find(x) == 0) {
                return true;
            }
        }
        return false;
    } else {
        return text.find(pref) == 0;
    }
}
int main() {
    auto candidate = f;
    assert(candidate(("Hello World"), ("W")) == (false));
}
