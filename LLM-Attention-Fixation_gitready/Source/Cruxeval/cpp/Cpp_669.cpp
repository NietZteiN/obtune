#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string t) {
    std::string sep = "-";
    std::size_t pos = t.rfind(sep);
    if (pos == std::string::npos) {
        return t;
    }
    std::string a = t.substr(0, pos);
    std::string b = t.substr(pos + 1);
    if (b.size() == a.size()) {
        return "imbalanced";
    } else {
        std::string result = a + b;
        std::string::iterator end_pos = std::remove(result.begin(), result.end(), '-');
        result.erase(end_pos, result.end());
        return result;
    }
}
int main() {
    auto candidate = f;
    assert(candidate(("fubarbaz")) == ("fubarbaz"));
}
