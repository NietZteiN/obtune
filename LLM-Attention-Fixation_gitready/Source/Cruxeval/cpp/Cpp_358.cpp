#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string text, std::string value) {
    std::vector<int> indexes;
    for (int i = 0; i < text.size(); i++) {
        if (text[i] == value[0] && (i == 0 || text[i - 1] != value[0])) {
            indexes.push_back(i);
        }
    }

    if (indexes.size() % 2 == 1) {
        return text;
    }

    return text.substr(indexes[0] + 1, indexes.back() - indexes[0] - 1);
}
int main() {
    auto candidate = f;
    assert(candidate(("btrburger"), ("b")) == ("tr"));
}
