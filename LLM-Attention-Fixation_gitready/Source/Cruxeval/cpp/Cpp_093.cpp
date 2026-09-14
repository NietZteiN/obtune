#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string n) {
    int length = n.length() + 2;
    std::vector<char> revn(n.begin(), n.end());
    std::string result(revn.begin(), revn.end());
    revn.clear();
    return result + std::string(length, '!');
}
int main() {
    auto candidate = f;
    assert(candidate(("iq")) == ("iq!!!!"));
}
