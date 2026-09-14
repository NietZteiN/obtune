#include<assert.h>
#include<bits/stdc++.h>
long f(std::vector<long> lst, long start, long end) {
    long count = 0;
    for (long i = start; i < end; i++) {
        for (long j = i; j < end; j++) {
            if (lst[i] != lst[j]) {
                count++;
            }
        }
    }
    return count;
}
int main() {
    auto candidate = f;
    assert(candidate((std::vector<long>({(long)1, (long)2, (long)4, (long)3, (long)2, (long)1})), (0), (3)) == (3));
}
