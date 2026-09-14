#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string a, std::string b, long n) {
    std::string result = b;
    std::string m = b;
    for (int i = 0; i < n; i++) {
        if (!m.empty()) {
            size_t pos = a.find(m);
            if (pos != std::string::npos) {
                a.erase(pos, m.length());
                m.clear();
            }
            result = m = b;
        }
    }
    std::stringstream ss(a);
    std::string token;
    std::string res;
    while (std::getline(ss, token, b[0])) {
        res += token;
    }
    return res;
}
int main() {
    auto candidate = f;
    assert(candidate(("unrndqafi"), ("c"), (2)) == ("unrndqafi"));
}
