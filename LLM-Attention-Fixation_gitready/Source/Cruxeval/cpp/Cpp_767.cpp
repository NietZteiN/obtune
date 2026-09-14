#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string text) {
    std::stringstream ss(text);
    std::vector<std::string> a;
    std::string word;
    while (ss >> word) {
        a.push_back(word);
    }

    for (int i = 0; i < a.size(); i++) {
        if (std::all_of(a[i].begin(), a[i].end(), ::isdigit) == false) {
            return "-";
        }
    }

    return std::accumulate(a.begin(), a.end(), std::string(), [](const std::string& left, const std::string& right) {
        return left + (left.empty() ? "" : " ") + right;
    });
}
int main() {
    auto candidate = f;
    assert(candidate(("d khqw whi fwi bbn 41")) == ("-"));
}
