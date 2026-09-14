#include<assert.h>
#include<bits/stdc++.h>
long f(std::string text) {
    int max_index = -1;
    for (char ch : {'a', 'e', 'i', 'o', 'u'}) {
        int index = text.find(ch);
        if (index > max_index) {
            max_index = index;
        }
    }
    return max_index;
}
int main() {
    auto candidate = f;
    assert(candidate(("qsqgijwmmhbchoj")) == (13));
}
