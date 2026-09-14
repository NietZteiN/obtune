#include<assert.h>
#include<bits/stdc++.h>
long f(std::string x) {
    int a = 0;
    std::stringstream ss(x);
    std::string word;
    while (ss >> word) {
        a += word.size() * 2;
    }
    return a;
}
int main() {
    auto candidate = f;
    assert(candidate(("999893767522480")) == (30));
}
