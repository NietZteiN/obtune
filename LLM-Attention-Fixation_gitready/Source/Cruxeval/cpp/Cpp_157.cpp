#include<assert.h>
#include<bits/stdc++.h>
long f(std::string phrase) {
    int ans = 0;
    for (char& ch : phrase) {
        if (ch == '0') {
            ans++;
        }
    }
    return ans;
}
int main() {
    auto candidate = f;
    assert(candidate(("aboba 212 has 0 digits")) == (1));
}
