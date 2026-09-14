#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string line) {
    int count = 0;
    std::string a;
    for (int i = 0; i < line.length(); i++) {
        count += 1;
        if (count%2==0) {
            a.push_back(tolower(line[i]) == line[i] ? toupper(line[i]) : tolower(line[i]));
        }
        else {
            a.push_back(line[i]);
        }
    }
    return a;
}
int main() {
    auto candidate = f;
    assert(candidate(("987yhNSHAshd 93275yrgSgbgSshfbsfB")) == ("987YhnShAShD 93275yRgsgBgssHfBsFB"));
}
