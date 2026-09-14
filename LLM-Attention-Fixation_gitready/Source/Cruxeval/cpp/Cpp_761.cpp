#include<assert.h>
#include<bits/stdc++.h>
std::vector<long> f(std::vector<long> array) {
    std::vector<long> output = array;
    for (int i = 0; i < output.size(); i += 2) {
        output[i] = output[output.size() - 1 - i];
    }
    std::reverse(output.begin(), output.end());
    return output;
}
int main() {
    auto candidate = f;
    assert(candidate((std::vector<long>())) == (std::vector<long>()));
}
