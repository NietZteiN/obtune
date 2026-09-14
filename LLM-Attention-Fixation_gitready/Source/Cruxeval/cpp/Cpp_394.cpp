#include<assert.h>
#include<bits/stdc++.h>
long f(std::string text) {
    std::stringstream ss(text);
    std::string line;
    int i = 0;
    while (std::getline(ss, line)) {
        if (line.empty()) {
            return i;
        }
        i++;
    }
    return -1;
}
int main() {
    auto candidate = f;
    assert(candidate(("2 m2 \n\nbike")) == (1));
}
