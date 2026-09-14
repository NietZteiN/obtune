#include<assert.h>
#include<bits/stdc++.h>
long f(std::string text) {
    int m = 0;
    int cnt = 0;
    std::stringstream ss(text);
    std::string word;
    while (ss >> word) {
        if (word.length() > m) {
            cnt++;
            m = word.length();
        }
    }
    return cnt;
}
int main() {
    auto candidate = f;
    assert(candidate(("wys silak v5 e4fi rotbi fwj 78 wigf t8s lcl")) == (2));
}
