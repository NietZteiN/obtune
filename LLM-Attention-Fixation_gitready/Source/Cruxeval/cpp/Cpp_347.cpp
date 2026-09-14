#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string text) {
    std::vector<char> ls(text.begin(), text.end());
    int length = ls.size();
    for (int i = 0; i < length; i++) {
        ls.insert(ls.begin() + i, ls[i]);
    }
    return std::string(ls.begin(), ls.end()).append(length * 2 - ls.size(), ' ');
}
int main() {
    auto candidate = f;
    assert(candidate(("hzcw")) == ("hhhhhzcw"));
}
