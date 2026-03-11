# pi500pl-kbmon
pi500plus activity displayed on keyboard leds

## How it works

__Disk IO__

```python
#psutil.disk_io_counters () Results
{'read_count': 100590,
 'write_count': 76135,
 'read_bytes': 4308303872,
 'write_bytes': 1918784000,
 'read_time': 37735,
 'write_time': 249701,
 'read_merged_count': 39321,
 'write_merged_count': 96243,
 'busy_time': 52472}
```
Results are dependent on 2 readings taken at a fixed interval (SLEEP_TIME).
- The byte_io activity is calculated: (read_bytes(curr) - read_bytes(prev)) + (write_bytes(curr) - write_bytes(prev))
  - if byte_io \< BYTE_IO_MIN, key is set to NORMAL_COLOR.
  - if byte_io \>= BYTE_IO_MAX, the key is set to CRITICAL_COLOR.
  - Otherwise the key is set to CRITICAL with a brightness adjusted by the ratio of byte_io to BYTE_IO_MAX.

- Notes
  - If SLEEP_TIME is changed the BYTE_IO_* constants need to be adjusted.

__CPU load__

```python
#psutil.cpu_percent() Results
78.6
```

__Temperatures__

```python
# psutil.sensors_temperatures() results:
{'cpu_thermal': 
  [shwtemp(label='',
           current=43.55,
           high=None,
           critical=None)],
'nvme':
  [shwtemp(label='Composite',
           current=39.85,
           high=82.85,
           critical=84.85),
   shwtemp(label='Sensor 1',
           current=39.85,
           high=65261.85,
           critical=65261.85)],
'rp1_adc':
  [shwtemp(label='',
           current=52.567,
           high=None,
           critical=None)]
 }
```
- __CPU__
  - cpu_temp \< CPU_TEMP_WARN, key is set to NORMAL_COLOR
  - cpu_temp \>= CPU_TEMP_WARN, and \< CPU_TEMP_CRITICAL, key is set to WARNING_COLOR
  - cpu_temp \>= CPU_TEMP_WARN, key is set to CCRITICAL_COLOR

- __NVME__
  - nvme_temp \< NVME_TEMP_WARN,key is set to NORMAL_COLOR
  - nvme_temp \>= NVME_TEMP_WARN and \< NVME_TEMP_CRITICAL, key is set to WARNING_COLOR
  - nvme_temp \>= NVME_TEMP_WARN, key is set to CRITICAL_COLOR

__Memory Usage__

```python
# psutil.virtual_memory() results:
svmem(total=16998400000,
      available=6184501248,
      percent=63.6,
      used=9559703552,
      free=1403568128,
      active=6955646976,
      inactive=7213350912,
      buffers=261849088,
      cached=5773279232,
      shared=995295232,
      slab=578404352)
```

- usage_pc (percent)
  - usage_pc \< MEMORY_WARN, key is set to NORMAL_COLOR
  - usage_pc \>= MEMORY_WARN and \< MEMORY_CRITICAL, key is set to WARNING_COLOR
  - usage_pc \>= MEMORY_WARN, key is set to CRITICAL_COLOR