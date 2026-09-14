#include<assert.h>
#include<bits/stdc++.h>
bool f(std::string x) {
    int n = x.size();
    int i = 0;
    while (i < n && isdigit(x[i])) {
        i++;
    }
    return i == n;
}
int main() {
    auto candidate = f;
    assert(candidate(("1")) == (true));
}
