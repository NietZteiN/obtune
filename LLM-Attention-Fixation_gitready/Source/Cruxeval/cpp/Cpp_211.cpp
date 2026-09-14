#include<assert.h>
#include<bits/stdc++.h>
long f(std::string s) {
    int count = 0;
    for (char c : s) {
        if (s.find_last_of(c) != s.find_first_of(c)) {
            count++;
        }
    }
    return count;
}
int main() {
    auto candidate = f;
    assert(candidate(("abca dea ead")) == (10));
}
