#include<assert.h>
#include<bits/stdc++.h>
std::vector<long> f(std::string text) {
    std::map<char, long> d;
    for (char& c : text) {
        if (c == '-') continue;
        c = std::tolower(c);
        if (d.find(c) != d.end()) {
            d[c] += 1;
        } else {
            d[c] = 1;
        }
    }
    std::vector<std::pair<char, long>> items(d.begin(), d.end());
    std::sort(items.begin(), items.end(), [](auto& a, auto& b) { return a.second < b.second; });
    std::vector<long> result;
    for (auto& item : items) {
        result.push_back(item.second);
    }
    return result;
}
int main() {
    auto candidate = f;
    assert(candidate(("x--y-z-5-C")) == (std::vector<long>({(long)1, (long)1, (long)1, (long)1, (long)1})));
}
