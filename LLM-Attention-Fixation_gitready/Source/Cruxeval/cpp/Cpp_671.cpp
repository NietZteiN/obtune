#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string text, std::string char1, std::string char2) {
    std::string result = text;
    std::map<char, char> trans_map;
    for (int i = 0; i < char1.size(); i++) {
        trans_map[char1[i]] = char2[i];
    }

    for (auto& pair : trans_map) {
        std::replace(result.begin(), result.end(), pair.first, pair.second);
    }

    return result;
}
int main() {
    auto candidate = f;
    assert(candidate(("ewriyat emf rwto segya"), ("tey"), ("dgo")) == ("gwrioad gmf rwdo sggoa"));
}
