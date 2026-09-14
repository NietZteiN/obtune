#include<assert.h>
#include<bits/stdc++.h>
long f(std::string text, long s, long e) {
    std::string sublist = text.substr(s, e - s);
    if (sublist.empty()) {
        return -1;
    }
    return sublist.find_first_of(*std::min_element(sublist.begin(), sublist.end()));
}
int main() {
    auto candidate = f;
    assert(candidate(("happy"), (0), (3)) == (1));
}
