#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::vector<std::string> array) {
    if (array.size() == 1) {
        return array[0];
    }
    std::vector<std::string> result(array.begin(), array.end());
    int i = 0;
    while (i < array.size() - 1) {
        for (int j = 0; j < 2; ++j) {
            result[i * 2] = array[i];
            i++;
        }
    }
    return std::accumulate(result.begin(), result.end(), std::string(""));
}
int main() {
    auto candidate = f;
    assert(candidate((std::vector<std::string>({(std::string)"ac8", (std::string)"qk6", (std::string)"9wg"}))) == ("ac8qk6qk6"));
}
