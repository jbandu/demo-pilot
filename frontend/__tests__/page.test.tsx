import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import HomePage from '@/app/page'
import { useRouter } from 'next/navigation'

jest.mock('next/navigation', () => ({
  useRouter: jest.fn(),
}))

describe('HomePage', () => {
  beforeEach(() => {
    (useRouter as jest.Mock).mockReturnValue({
      push: jest.fn(),
    })
  })

  it('renders the main heading', () => {
    render(<HomePage />)
    expect(screen.getByText('Demo Copilot')).toBeInTheDocument()
  })

  it('displays demo type selection cards', () => {
    render(<HomePage />)
    expect(screen.getByText('InSign')).toBeInTheDocument()
    expect(screen.getByText('Crew Intelligence')).toBeInTheDocument()
  })

  it('requires email before starting demo', () => {
    render(<HomePage />)
    const startButton = screen.getByRole('button', { name: /start ai demo/i })
    expect(startButton).toBeDisabled()
  })

  it('enables start button when email is provided', () => {
    render(<HomePage />)

    const emailInput = screen.getByPlaceholderText('you@company.com')
    fireEvent.change(emailInput, { target: { value: 'test@example.com' } })

    const startButton = screen.getByRole('button', { name: /start ai demo/i })
    expect(startButton).not.toBeDisabled()
  })

  it('calls API and navigates on demo start', async () => {
    const mockPush = jest.fn()
    ;(useRouter as jest.Mock).mockReturnValue({
      push: mockPush,
    })

    global.fetch = jest.fn(() =>
      Promise.resolve({
        ok: true,
        json: () => Promise.resolve({ session_id: 'test-123' }),
      })
    ) as jest.Mock

    render(<HomePage />)

    const emailInput = screen.getByPlaceholderText('you@company.com')
    fireEvent.change(emailInput, { target: { value: 'test@example.com' } })

    const startButton = screen.getByRole('button', { name: /start ai demo/i })
    fireEvent.click(startButton)

    await waitFor(() => {
      expect(mockPush).toHaveBeenCalledWith('/demo/test-123')
    })
  })
})
