#include<assert.h>
#include<bits/stdc++.h>
long f(std::string val, std::string text) {
    std::vector<int> indices;
    for (int index = 0; index < text.length(); ++index) {
        if (text[index] == val[0]) {
            indices.push_back(index);
        }
    }
    if (indices.size() == 0) {
        return -1;
    } else {
        return indices[0];
    }
}
int main() {
    auto candidate = f;
    assert(candidate(("o"), ("fnmart")) == (-1));
}
