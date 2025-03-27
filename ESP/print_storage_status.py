import uos


def get_storage_info():
    fs_stat = uos.statvfs('/')
    return {
        'block_size': fs_stat[0],          # Filesystem block size
        'total_blocks': fs_stat[2],        # Total blocks
        'free_blocks': fs_stat[3],         # Free blocks
        'total_bytes': fs_stat[2] * fs_stat[0],
        'free_bytes': fs_stat[3] * fs_stat[0],
        'used_percent': 100 - (fs_stat[3] / fs_stat[2] * 100)
    }

# Example usage:
storage = get_storage_info()
print(storage)
print(f"Free: {storage['free_bytes']/1024:.1f}KB / {storage['total_bytes']/1024:.1f}KB")